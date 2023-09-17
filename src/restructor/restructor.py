import os
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

    def _create_new_root_folder(
        self, metadata: Metadata, target_path: str
    ) -> RestructedFolder:
        root_folder_title = self._formatter._format_name(name=metadata.get_title())

        new_root_absoluth_path = os.path.join(target_path, root_folder_title)

        return RestructedFolder(absolute_path=new_root_absoluth_path)


class MovieRestructor(GeneralRestructor):
    def restruct(self, metadata: MovieMetadata, target_path: str) -> RestructedFolder:
        if not os.path.exists(path=target_path):
            raise DirectoryNotFoundException

        new_root_folder = self._create_new_root_folder(
            metadata=metadata, target_path=target_path
        )

        self._restruct_subtitle(
            root_folder=new_root_folder,
            subtitles=metadata.get_subtitles(),
            metadata=metadata,
        )
        self._restruct_mediafile(root_folder=new_root_folder, metadata=metadata)

        return new_root_folder

    def _restruct_subtitle(
        self,
        root_folder: RestructedFolder,
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

                root_folder.append_struct(
                    RestructedFile(
                        absolute_path=new_file_path,
                        original_file=selected_subtitle_file,
                    )
                )

                # TODO: Backup subtitle
                # subtitle_backup = self._create_subtitle_backup_folder(
                #     subtitle=subtitle_struct,
                #     new_root_path=root_folder.get_absolute_path(),
                # )
                # root_folder.append_struct(subtitle_backup)

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

    def _create_subtitle_backup_folder(
        self, subtitle: Structable, new_root_path: str
    ) -> RestructedFolder:
        backup_path = os.path.join(new_root_path, "SubtitleBackup")

        subtitle_backup = RestructedFolder(absolute_path=backup_path)
        subtitle_backup.append_struct(subtitle)

        return subtitle_backup

    def _restruct_mediafile(
        self, root_folder: RestructedFolder, metadata: MovieMetadata
    ) -> None:
        index = 1

        for file in metadata.get_media_files():
            new_title = metadata.get_title()

            # Add index if multiple movie file exists
            if len(metadata.get_media_files()) > 1:
                new_title = f"{new_title}({index})"
                index += 1

            new_file_name = new_title + "." + file.get_extension()
            new_path = os.path.join(root_folder.get_absolute_path(), new_file_name)

            root_folder.append_struct(
                struct=RestructedFile(absolute_path=new_path, original_file=file)
            )


class TVRestructor(GeneralRestructor):
    pass
