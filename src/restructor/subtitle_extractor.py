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

    def extract_archived_subtitle(self, subtitle: File, metadata: Metadata) -> Folder:
        if subtitle.get_file_type() != FileType.ARCHIVED_SUBTITLE:
            raise InvalidMediaTypeException

        temp_extracted_subtitle_path = tempfile.TemporaryDirectory(
            suffix=metadata.get_title()
        ).name

        extract_archive(
            archive=subtitle.get_absolute_path(),
            verbosity=-1,
            outdir=temp_extracted_subtitle_path,
        )

        return self._constrcutor.struct(source_path=temp_extracted_subtitle_path)
