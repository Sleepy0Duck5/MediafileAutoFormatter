from typing import Optional

from src.model.metadata import Metadata, MovieMetadata, TVMetadata
from src.model.folder import Folder
from src.model.structable import Structable
from src.constants import MediaType
from src.errors import MetadataBuildException


class MetadataBuilder:
    def __init__(self) -> None:
        self._title = None
        self._original_title = None
        self._media_type = None
        self._root_path = None
        self._media_root = None
        self._subtitles = None
        self._seasons = None

    def set_title(self, title: str):
        self._title = title

    def set_original_title(self, original_title: str):
        self._original_title = original_title

    def set_media_type(self, media_type: MediaType):
        self._media_type = media_type

    def set_root_path(self, root_path: str):
        self._root_path = root_path

    def set_media_root(self, media_root: Folder):
        self._media_root = media_root

    def set_subtitles(self, subtitles: Optional[dict[str, Structable]]):
        self._subtitles = subtitles

    def set_seasons(self, seasons: dict[str, Folder]):
        self._seasons = seasons

    def build(self) -> Metadata:
        if not self._title:
            raise MetadataBuildException

        if not self._original_title:
            raise MetadataBuildException

        if not self._media_type:
            raise MetadataBuildException

        if not self._root_path:
            raise MetadataBuildException

        if not self._title:
            raise MetadataBuildException

        if not self._media_root:
            raise MetadataBuildException

        if not self._subtitles:
            raise MetadataBuildException

        if self._media_type == MediaType.MOVIE:
            return MovieMetadata(
                title=self._title,
                original_title=self._original_title,
                media_type=self._media_type,
                root_path=self._root_path,
                media_root=self._media_root,
                subtitles=self._subtitles,
            )

        if self._media_type == MediaType.TV:
            if not self._seasons:
                raise MetadataBuildException

            return TVMetadata(
                title=self._title,
                original_title=self._original_title,
                media_type=self._media_type,
                root_path=self._root_path,
                media_root=self._media_root,
                subtitles=self._subtitles,
                seasons=self._seasons,
            )

        raise NotImplementedError
