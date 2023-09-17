from typing import List

from src.model.metadata import Metadata, MovieMetadata, TVMetadata, SeasonMetadata
from src.model.folder import Folder
from src.model.file import File
from src.model.structable import Structable
from src.constants import MediaType
from src.analyzer.error import MetadataBuildException


class MetadataBuilder:
    def __init__(self) -> None:
        self._title: str
        self._original_title: str
        self._root: Folder
        self._media_root: Folder

    def set_title(self, title: str):
        self._title = title

    def get_title(self) -> str:
        return self._title

    def set_original_title(self, original_title: str):
        self._original_title = original_title

    def set_root(self, root: Folder):
        self._root = root

    def get_root(self) -> Folder:
        return self._root

    def set_media_root(self, media_root: Folder):
        self._media_root = media_root

    def get_media_root(self) -> Folder:
        return self._media_root

    def _build_validation(self) -> None:
        if not self._title:
            raise MetadataBuildException

        if not self._original_title:
            raise MetadataBuildException

        if not self._root:
            raise MetadataBuildException

        if not self._title:
            raise MetadataBuildException

        if not self._media_root:
            raise MetadataBuildException

    def build(self) -> Metadata:
        raise NotImplementedError


class MovieMetadataBuilder(MetadataBuilder):
    def __init__(self, media_type: MediaType) -> None:
        super().__init__()
        self._subtitles: List[Structable]
        self._media_type = media_type

    def set_subtitles(self, subtitles: List[Structable]) -> None:
        self._subtitles = subtitles

    def set_media_files(self, media_files: List[File]) -> None:
        self._media_files = media_files

    def _build_validation(self) -> None:
        super()._build_validation()

        if not self._media_files:
            raise MetadataBuildException

    def build(self) -> Metadata:
        self._build_validation()

        return MovieMetadata(
            title=self._title,
            original_title=self._original_title,
            root=self._root,
            media_root=self._media_root,
            media_files=self._media_files,
            subtitles=self._subtitles,
        )


class TVMetadataBuilder(MetadataBuilder):
    def __init__(self) -> None:
        super().__init__()
        self._seasons: dict[int, SeasonMetadata] = {}
        self._media_type = MediaType.TV

    def set_seasons(self, seasons: dict[int, SeasonMetadata]):
        self._seasons = seasons

    def _build_validation(self) -> None:
        super()._build_validation()

        if not self._seasons:
            raise MetadataBuildException

    def build(self) -> Metadata:
        self._build_validation()

        return TVMetadata(
            title=self._title,
            original_title=self._original_title,
            root=self._root,
            media_root=self._media_root,
            seasons=self._seasons,
        )
