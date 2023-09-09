import os
from abc import ABCMeta
from patoolib import extract_archive
from loguru import logger
from typing import List, Optional

from src.model.structable import Structable
from src.model.file import File
from src.model.folder import Folder, RestructedFolder
from src.model.metadata import Metadata, MovieMetadata
from src.formatter.formatter import Formatter
from src.restructor.resturct_logger import GeneralRestructLogger
from src.restructor.subtitle_extractor import (
    SubtitleExtractor,
    GeneralSubtitleExtractor,
)
from src.env_configs import EnvConfigs
from src.errors import TargetPathNotFoundException, InvalidMediaTypeException
from src.constants import FileType, Constants


class Restructor(metaclass=ABCMeta):
    def __init__(self, env_configs: EnvConfigs, formatter: Formatter) -> None:
        raise NotImplementedError

    def restruct(self, metadata: Metadata, target_path: str) -> Folder:
        raise NotImplementedError

    def _extract_subtitles(self, metadata: Metadata) -> dict[int, Folder]:
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
        self._restruct_logger = GeneralRestructLogger()
        self._subtitle_extractor = subtitle_extractor

    def _create_new_root_folder(
        self, metadata: Metadata, target_path: str
    ) -> RestructedFolder:
        root_folder_title = self._formatter._format_name(name=metadata.get_title())

        new_root_absoluth_path = os.path.join(target_path, root_folder_title)

        return RestructedFolder(absolute_path=new_root_absoluth_path)


class MovieRestructor(GeneralRestructor):
    def restruct(self, metadata: MovieMetadata, target_path: str) -> Folder:
        if not os.path.exists(path=target_path):
            raise TargetPathNotFoundException

        root_folder = self._create_new_root_folder(
            metadata=metadata, target_path=target_path
        )

        self._restruct_subtitle(root_folder=root_folder, metadata=metadata)
        self._restruct_mediafile(root_folder=root_folder, metadata=metadata)

        return root_folder

    def _restruct_subtitle(
        self, root_folder: RestructedFolder, metadata: MovieMetadata
    ) -> None:
        subtitles = metadata.get_subtitles()

        if subtitles:
            subtitle_folder = self._extract_subtitles(metadata=metadata)
            if not subtitle_folder:
                for subtitle in subtitles:
                    if isinstance(subtitle, Folder):
                        subtitle_folder = subtitle
                        break

            if subtitle_folder:
                selected_subtitle = self._select_subtitle(folder=subtitle_folder)
                if selected_subtitle:
                    root_folder.append_struct(selected_subtitle)

    def _extract_subtitles(self, metadata: MovieMetadata) -> Optional[Folder]:
        subtitles = metadata.get_subtitles()

        for subtitle in subtitles:
            if (
                isinstance(subtitle, File)
                and subtitle.get_file_type() == FileType.ARCHIVED_SUBTITLE
            ):
                extracted_folder = self._subtitle_extractor.extract_archived_subtitle(
                    subtitle=subtitle, metadata=metadata
                )

                return extracted_folder

        return None

    def _select_subtitle(self, folder: Folder) -> Optional[File]:
        for subtitle in folder.get_files():
            if subtitle.get_file_type() == FileType.SUBTITLE:
                return subtitle

        return None

    def _restruct_mediafile(
        self, root_folder: RestructedFolder, metadata: MovieMetadata
    ) -> None:
        for file in metadata.get_media_root().get_files():
            if file.get_file_type() == FileType.MEDIA:
                root_folder.append_struct(struct=file)
                break


class TVRestructor(GeneralRestructor):
    pass
