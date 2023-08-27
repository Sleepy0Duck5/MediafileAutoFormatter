from abc import ABCMeta
from typing import Optional

from src.constants import MediaType
from src.model.folder import Folder
from src.model.structable import Structable


class Metadata(metaclass=ABCMeta):
    def __init__(
        self,
        title: str,
        original_title: str,
        media_type: MediaType,
        root_path: str,
        media_root: Folder,
        subtitles: Optional[dict[str, Structable]],
    ) -> None:
        self._title = title
        self._original_title = original_title
        self._media_type = media_type
        self._root_path = root_path
        self._media_root = media_root
        self._subtitles = subtitles


class MovieMetadata(Metadata):
    def __init__(
        self,
        title: str,
        original_title: str,
        media_type: MediaType,
        root_path: str,
        media_root: Folder,
        subtitles: Optional[dict[str, Structable]],
    ) -> None:
        super().__init__(
            title, original_title, media_type, root_path, media_root, subtitles
        )


class TVMetadata(Metadata):
    def __init__(
        self,
        title: str,
        original_title: str,
        media_type: MediaType,
        root_path: str,
        media_root: Folder,
        subtitles: Optional[dict[str, Structable]],
        seasons: dict[str, Folder],
    ) -> None:
        super().__init__(
            title, original_title, media_type, root_path, media_root, subtitles
        )
        self._seasons = seasons
