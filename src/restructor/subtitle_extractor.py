import os
import random
import tempfile
from abc import ABCMeta
from patoolib import extract_archive
from typing import List

from src.model.structable import Structable
from src.model.file import File
from src.model.folder import Folder
from src.model.metadata import (
    Metadata,
    SubtitleContainingMetadata,
)
from src.constructor.constructor import Constructor
from src.errors import InvalidMediaTypeException
from src.constants import FileType


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

        temp_extracted_subtitle_path = tempfile.mkdtemp()

        extract_archive(
            archive=subtitle.get_absolute_path(),
            verbosity=-1,
            outdir=temp_extracted_subtitle_path,
        )

        return self._constrcutor.struct(source_path=temp_extracted_subtitle_path)
