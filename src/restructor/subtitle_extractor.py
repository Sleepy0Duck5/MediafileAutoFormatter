import os
from abc import ABCMeta
from patoolib import extract_archive
from loguru import logger
from typing import List, Optional
import tempfile

from src.model.structable import Structable
from src.model.file import File
from src.model.folder import Folder, RestructedFolder
from src.model.metadata import (
    Metadata,
    SubtitleContainingMetadata,
)
from src.constructor.constructor import Constructor
from src.formatter.formatter import Formatter
from src.env_configs import EnvConfigs
from src.errors import InvalidMediaTypeException, InvalidMetadataTypeException
from src.constants import FileType, Constants, MediaType


class SubtitleExtractor(metaclass=ABCMeta):
    def __init__(self) -> None:
        raise NotImplementedError

    def get_subtitle(self, metadata: SubtitleContainingMetadata) -> List[Structable]:
        raise NotImplementedError

    def extract_archived_subtitle(self, subtitle: File, metadata: Metadata) -> Folder:
        raise NotImplementedError


class GeneralSubtitleExtractor(SubtitleExtractor):
    def __init__(self, constrcutor: Constructor) -> None:
        self._constrcutor = constrcutor

    # def get_subtitle(self, metadata: Metadata) -> List[Structable]:
    #     if isinstance(metadata, MovieMetadata):
    #         return self._get_subtitle_from_subtitle_containing_metadata(
    #             metadata=metadata
    #         )

    #     if isinstance(metadata, TVMetadata):
    #         return self._get_subtitle_from_tv_metadata(metadata=metadata)

    #     logger.warning(f"get_subtitle not implemented for {str(metadata.__class__)}")
    #     return []

    # def _get_subtitle_from_subtitle_containing_metadata(
    #     self, metadata: SubtitleContainingMetadata
    # ) -> List[Structable]:
    #     if not isinstance(metadata, SubtitleContainingMetadata):
    #         raise InvalidMetadataTypeException

    #     for subtitle in metadata.get_subtitles():
    #         if isinstance(subtitle, File):
    #             if subtitle.get_file_type() == FileType.ARCHIVED_SUBTITLE:
    #                 extracted_folder = self._extract_archived_subtitle(
    #                     subtitle=subtitle, metadata=metadata
    #                 )

    #                 return [extracted_folder]
    #         else:
    #             logger.warning("Subtitle folder found but not supported.")

    #     subtitle_files = []
    #     for subtitle in metadata.get_subtitles():
    #         if (
    #             isinstance(subtitle, File)
    #             and subtitle.get_file_type() == FileType.SUBTITLE
    #         ):
    #             subtitle_files.append(subtitle)

    #     return subtitle_files

    # def _get_subtitle_from_tv_metadata(self, metadata: TVMetadata) -> List[Structable]:
    #     if not isinstance(metadata, TVMetadata):
    #         raise InvalidMetadataTypeException

    #     seasons = metadata.get_seasons()

    #     extracted_subtitle_folders = []
    #     for season_index in seasons:
    #         season_metadata = seasons.get(season_index)
    #         if season_metadata:
    #             self._get_subtitle_from_subtitle_containing_metadata(
    #                 metadata=season_metadata
    #             )

    #     return extracted_subtitle_folders

    def extract_archived_subtitle(self, subtitle: File, metadata: Metadata) -> Folder:
        if subtitle.get_file_type() != FileType.ARCHIVED_SUBTITLE:
            raise InvalidMediaTypeException

        temp_extracted_subtitle_path = tempfile.TemporaryDirectory().name

        extract_archive(
            archive=subtitle.get_absolute_path(),
            verbosity=-1,
            outdir=temp_extracted_subtitle_path,
        )

        return self._constrcutor.struct(source_path=temp_extracted_subtitle_path)
