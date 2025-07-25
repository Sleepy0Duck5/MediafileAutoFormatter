import os
import tempfile
import shutil
from abc import ABCMeta
from loguru import logger
from typing import List
from datetime import datetime

from src.model.structable import Structable
from src.model.file import File, RestructedFile
from src.model.folder import Folder, RestructedFolder
from src.model.metadata import (
    Metadata,
    SubtitleContainingMetadata,
)
from src.formatter.formatter import Formatter
from src.formatter.subtitle_converter import SubtitleConverter
from src.restructor.subtitle_extractor import (
    SubtitleExtractor,
)
from src.env_configs import EnvConfigs
from src.errors import DirectoryNotFoundException
from src.constants import FileType, Constants, Extensions


class Restructor(metaclass=ABCMeta):
    def __init__(self, env_configs: EnvConfigs, formatter: Formatter) -> None:
        raise NotImplementedError

    def restruct(self, metadata: Metadata, target_path: str) -> RestructedFolder:
        raise NotImplementedError

    def _extract_subtitle(self, metadata: Metadata) -> dict[int, Folder]:
        raise NotImplementedError


class GeneralRestructor(Restructor):
    def __init__(
        self,
        env_configs: EnvConfigs,
        formatter: Formatter,
        subtitle_extractor: SubtitleExtractor,
        subtitle_converter: SubtitleConverter,
    ) -> None:
        self._env_configs = env_configs
        self._formatter = formatter
        self._subtitle_extractor = subtitle_extractor
        self._subtitle_converter = subtitle_converter
        self._log = ""

    def restruct(self, metadata: Metadata, target_path: str) -> Folder:
        if not os.path.exists(path=target_path):
            raise DirectoryNotFoundException

        self._log += metadata.explain() + "\n"

        root_folder = self._create_new_root_folder(
            metadata=metadata, target_path=target_path
        )

        return root_folder

    def _create_new_root_folder(self, metadata: Metadata, target_path: str) -> Folder:
        root_folder_title = self._formatter.format_name(name=metadata.get_title())

        new_root_absoluth_path = os.path.join(target_path, root_folder_title)

        new_root_folder = Folder(absolute_path=new_root_absoluth_path)

        self._append_restruct_log(new_root_folder)

        return new_root_folder

    def _export_restruct_log(self, root_folder: Folder) -> None:
        temp_file = tempfile.NamedTemporaryFile(delete=False)
        temp_file.write(self._log.encode("utf-8"))
        temp_file.flush()

        log_file_name = (
            f"MAF_Restruct_{datetime.now().strftime('%Y-%m-%d-%H-%M-%S')}.log"
        )
        log_path = os.path.join(root_folder.get_absolute_path(), log_file_name)
        log_file = RestructedFile(
            absolute_path=log_path,
            original_file=File(absolute_path=temp_file.name, file_type=FileType.EXTRA),
        )

        try:
            os.chmod(temp_file.name, Constants.DEFAULT_PERMISSION_FOR_LOG_FILE)
        except Exception as e:
            logger.warning(
                f"Failed to grant permission {Constants.DEFAULT_PERMISSION_FOR_LOG_FILE} to {temp_file.name}, error : {str(e)}"
            )

        root_folder.append_struct(log_file)
        self._log = ""

    def _restruct_subtitle(
        self,
        root_folder: Folder,
        subtitles: List[Structable],
        metadata: Metadata,
    ) -> None:
        """Add subtitle file to root_folder after converting subtitle format(smi -> srt/ass) and filename."""
        raise NotImplementedError

    def _get_subtitle_files(
        self,
        subtitle_struct: Structable,
        metadata: Metadata,
    ) -> List[File]:
        subtitle_files = []

        if isinstance(subtitle_struct, File):
            if subtitle_struct.get_file_type() == FileType.SUBTITLE:
                subtitle_files = [subtitle_struct]
            elif subtitle_struct.get_file_type() == FileType.ARCHIVED_SUBTITLE:
                extracted_folder = self._subtitle_extractor.extract_archived_subtitle(
                    subtitle=subtitle_struct, metadata=metadata
                )
                subtitle_files = self._get_subtitles_from_folder(
                    folder=extracted_folder
                )
        elif isinstance(subtitle_struct, Folder):
            subtitle_files = self._get_subtitles_from_folder(folder=subtitle_struct)

        if len(subtitle_files) <= 0:
            logger.warning("Subtitle found but nothing selected")
            self._log += "[WARNING] Subtitle found but nothing selected"

        return self._convert_subtitle(subtitle_files=subtitle_files)

    def _convert_subtitle(self, subtitle_files: List[File]) -> List[File]:
        if (not self._env_configs._CONVERT_SMI) or (
            not self._env_configs._CONVERT_SMI_EXTENSION
        ):
            return subtitle_files

        result = []

        for subtitle_file in subtitle_files:
            if subtitle_file.get_extension() == Extensions.SMI:
                try:
                    converted_files = self._subtitle_converter.convert_subtitle(
                        file=subtitle_file
                    )
                    result.extend(converted_files)
                    logger.info(
                        f"smi subtitle converted into {self._env_configs._CONVERT_SMI_EXTENSION} : {subtitle_file.get_absolute_path()}"
                    )
                    self._log += (
                        f"[CONVERTED] smi subtitle converted into {self._env_configs._CONVERT_SMI_EXTENSION} : {subtitle_file.get_absolute_path()}"
                        + "\n"
                    )
                except Exception as e:
                    error_msg = f"[WARNING] Failed to convert subtitle : {subtitle_file.get_absolute_path()}, error_msg={e}"
                    logger.opt(exception=e).warning(error_msg)
                    self._log += error_msg
                    result.append(subtitle_file)
            else:
                result.append(subtitle_file)

        return result

    def _get_subtitles_from_folder(self, folder: Folder) -> List[File]:
        subtitles = []

        for subtitle in folder.get_files():
            if subtitle.get_file_type() == FileType.SUBTITLE:
                subtitles.append(subtitle)

        return subtitles

    def _subtitle_backup(
        self, subtitle_files: List[Structable], root_folder: Folder
    ) -> None:
        # Create backup folder
        backup_path = os.path.join(
            root_folder.get_absolute_path(), Constants.SUBTITLE_BACKUP_DIRECTORY_NAME
        )
        backup_folder = Folder(absolute_path=backup_path)

        for file in subtitle_files:
            if isinstance(file, File):
                # Copy subtitle file
                backup_file_name = file.get_absolute_path().split(sep=os.sep)[-1]

                temp_copied_subtitle_path = os.path.join(
                    tempfile.mkdtemp(),
                    backup_file_name,
                )
                shutil.copy2(file.get_absolute_path(), temp_copied_subtitle_path)

                backup_file = RestructedFile(
                    absolute_path=os.path.join(backup_path, backup_file_name),
                    original_file=File(
                        absolute_path=temp_copied_subtitle_path,
                        file_type=file.get_file_type(),
                    ),
                )

                self._append_struct_to_folder(folder=backup_folder, struct=backup_file)
            else:
                logger.warning("Subtitle folder backup not implemented")
                raise NotImplemented

        self._append_struct_to_folder(folder=root_folder, struct=backup_folder)

    def _restruct_mediafile(
        self, root_folder: Folder, metadata: SubtitleContainingMetadata
    ) -> None:
        raise NotImplementedError

    def _append_restruct_log(self, struct: Structable):
        self._log += struct.explain() + "\n"

    def _append_struct_to_folder(self, folder: Folder, struct: Structable) -> None:
        folder.append_struct(struct=struct)
        self._append_restruct_log(struct=struct)

    def _rename_subtitle_and_append(
        self, root_folder: Folder, metadata: Metadata, subtitle_files: List[File]
    ) -> None:
        raise NotImplementedError
