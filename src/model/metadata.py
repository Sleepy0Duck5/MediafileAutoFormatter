from abc import ABCMeta
from typing import Optional, List

from src.constants import MediaType
from src.model.folder import Folder
from src.model.structable import Structable


class Metadata(metaclass=ABCMeta):
    def __init__(
        self,
        title: str,
        original_title: str,
        media_type: MediaType,
        root: Folder,
        media_root: Folder,
    ) -> None:
        self._title = title
        self._original_title = original_title
        self._media_type = media_type
        self._root = root
        self._media_root = media_root


class MediaMetadata(Metadata):
    def __init__(
        self,
        title: str,
        original_title: str,
        root: Folder,
        media_root: Folder,
        subtitle: List[Structable],
    ) -> None:
        self._media_type = MediaType.MOVIE
        self._subtitle = subtitle
        super().__init__(title, original_title, self._media_type, root, media_root)


class SeasonMetadata(Metadata):
    def __init__(
        self,
        title: str,
        original_title: str,
        root: Folder,
        media_root: Folder,
        subtitle: List[Structable],
    ) -> None:
        self._media_type = MediaType.TV
        self._subtitle = subtitle
        super().__init__(title, original_title, self._media_type, root, media_root)


class TVMetadata(Metadata):
    def __init__(
        self,
        title: str,
        original_title: str,
        root: Folder,
        media_root: Folder,
        seasons: dict[int, SeasonMetadata],
    ) -> None:
        self._media_type = MediaType.TV
        self._seasons = seasons
        super().__init__(title, original_title, self._media_type, root, media_root)
