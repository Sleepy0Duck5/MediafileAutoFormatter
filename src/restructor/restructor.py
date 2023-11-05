import os
import tempfile
import shutil
from abc import ABCMeta
from loguru import logger
from typing import List, Optional

from src.model.structable import Structable
from src.model.file import File, RestructedFile
from src.model.folder import Folder, RestructedFolder
from src.model.metadata import Metadata, MovieMetadata
from src.formatter.formatter import Formatter
from src.restructor.subtitle_extractor import (
    SubtitleExtractor,
)
from src.env_configs import EnvConfigs
from src.errors import DirectoryNotFoundException
from src.constants import FileType


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
    ) -> None:
        self._env_configs = env_configs
        self._formatter = formatter
        self._subtitle_extractor = subtitle_extractor
        self._log = ""

    def _create_new_root_folder(self, metadata: Metadata, target_path: str) -> Folder:
        root_folder_title = self._formatter._format_name(name=metadata.get_title())

        new_root_absoluth_path = os.path.join(target_path, root_folder_title)

        new_root_folder = Folder(absolute_path=new_root_absoluth_path)

        self._append_restruct_log(new_root_folder)

        return new_root_folder

    def _create_restruct_log(self, root_folder: Folder) -> None:
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            temp_file.write(self._log.encode("utf-8"))
            temp_file.flush()

            log_path = os.path.join(root_folder.get_absolute_path(), "MAF_Restruct.log")
            log_file = RestructedFile(
                absolute_path=log_path,
                original_file=File(
                    absolute_path=temp_file.name, file_type=FileType.EXTRA
                ),
            )

            root_folder.append_struct(log_file)
            return

    def _append_restruct_log(self, struct: Structable):
        self._log += struct.explain() + "\n"

    def _append_struct_to_folder(self, folder: Folder, struct: Structable) -> None:
        folder.append_struct(struct=struct)
        self._append_restruct_log(struct=struct)


class MovieRestructor(GeneralRestructor):
    def restruct(self, metadata: MovieMetadata, target_path: str) -> Folder:
        if not os.path.exists(path=target_path):
            raise DirectoryNotFoundException

        self._log += metadata.explain() + "\n"

        new_root_folder = self._create_new_root_folder(
            metadata=metadata, target_path=target_path
        )

        self._restruct_subtitle(
            root_folder=new_root_folder,
            subtitles=metadata.get_subtitles(),
            metadata=metadata,
        )

        self._restruct_mediafile(root_folder=new_root_folder, metadata=metadata)

        self._create_restruct_log(root_folder=new_root_folder)

        return new_root_folder

    def _restruct_subtitle(
        self,
        root_folder: Folder,
        subtitles: List[Structable],
        metadata: Metadata,
    ) -> None:
        if len(subtitles) <= 0:
            return

        for subtitle_struct in subtitles:
            selected_subtitle_file = self._get_subtitle_file(
                subtitle=subtitle_struct, metadata=metadata
            )

            if selected_subtitle_file:
                new_file_name = (
                    metadata.get_title()
                    + "."
                    + self._env_configs._SUBTITLE_SUFFIX
                    + "."
                    + selected_subtitle_file.get_extension()
                )
                new_file_path = os.path.join(
                    root_folder.get_absolute_path(), new_file_name
                )

                restructed_subtitle_file = RestructedFile(
                    absolute_path=new_file_path,
                    original_file=selected_subtitle_file,
                )

                self._append_struct_to_folder(
                    folder=root_folder, struct=restructed_subtitle_file
                )

                # TODO: Backup subtitle
                subtitle_backup_folder = self._subtitle_backup(
                    original_subtitle=subtitle_struct,
                    root_path=root_folder.get_absolute_path(),
                )

                self._append_struct_to_folder(
                    folder=root_folder, struct=subtitle_backup_folder
                )
                return

    def _get_subtitle_file(
        self,
        subtitle: Structable,
        metadata: Metadata,
    ) -> Optional[File]:
        if isinstance(subtitle, File):
            if subtitle.get_file_type() == FileType.SUBTITLE:
                return subtitle

            if subtitle.get_file_type() == FileType.ARCHIVED_SUBTITLE:
                extracted_folder = self._subtitle_extractor.extract_archived_subtitle(
                    subtitle=subtitle, metadata=metadata
                )
                return self._select_subtitle_from_folder(folder=extracted_folder)

            raise NotImplementedError

        if isinstance(subtitle, Folder):
            return self._select_subtitle_from_folder(folder=subtitle)

        raise NotImplementedError

    def _select_subtitle_from_folder(self, folder: Folder) -> Optional[File]:
        for subtitle in folder.get_files():
            if subtitle.get_file_type() == FileType.SUBTITLE:
                return subtitle

        return None

    def _subtitle_backup(self, original_subtitle: Structable, root_path: str) -> Folder:
        if isinstance(original_subtitle, File):
            # Copy subtitle file
            backup_file_name = original_subtitle.get_absolute_path().split(sep=os.sep)[
                -1
            ]
            temp_copied_subtitle_path = os.path.join(
                tempfile.gettempdir(),
                backup_file_name,
            )
            shutil.copy2(
                original_subtitle.get_absolute_path(), temp_copied_subtitle_path
            )

            # Create backup folder
            backup_path = os.path.join(root_path, "MAF_SubtitleBackup")

            backup_file = RestructedFile(
                absolute_path=os.path.join(backup_path, backup_file_name),
                original_file=File(
                    absolute_path=temp_copied_subtitle_path,
                    file_type=original_subtitle.get_file_type(),
                ),
            )

            backup_folder = Folder(absolute_path=backup_path)
            self._append_struct_to_folder(folder=backup_folder, struct=backup_file)
        else:
            logger.warning("Subtitle folder backup not implemented")
            raise NotImplemented

        return backup_folder

    def _restruct_mediafile(self, root_folder: Folder, metadata: MovieMetadata) -> None:
        index = 1

        for file in metadata.get_media_files():
            new_title = metadata.get_title()

            # Add index if multiple movie file exists
            if len(metadata.get_media_files()) > 1:
                new_title = f"{new_title}({index})"
                index += 1

            new_file_name = new_title + "." + file.get_extension()
            new_path = os.path.join(root_folder.get_absolute_path(), new_file_name)

            restructed_media_file = RestructedFile(
                absolute_path=new_path, original_file=file
            )

            self._append_struct_to_folder(
                folder=root_folder, struct=restructed_media_file
            )


class TVRestructor(GeneralRestructor):
    pass
