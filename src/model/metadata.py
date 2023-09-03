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

    def get_title(self) -> str:
        return self._title

    def get_original_title(self) -> str:
        return self._original_title

    def get_media_type(self) -> MediaType:
        return self._media_type

    def get_root(self) -> Folder:
        return self._root

    def get_media_root(self) -> Folder:
        return self._media_root


class MovieMetadata(Metadata):
    def __init__(
        self,
        title: str,
        original_title: str,
        root: Folder,
        media_root: Folder,
        subtitles: List[Structable],
    ) -> None:
        self._media_type = MediaType.MOVIE
        self._subtitles = subtitles
        super().__init__(title, original_title, self._media_type, root, media_root)

    def get_subtitles(self) -> List[Structable]:
        return self._subtitles


class SeasonMetadata(Metadata):
    def __init__(
        self,
        title: str,
        original_title: str,
        root: Folder,
        media_root: Folder,
        subtitles: List[Structable],
    ) -> None:
        self._media_type = MediaType.TV
        self._subtitles = subtitles
        super().__init__(title, original_title, self._media_type, root, media_root)

    def get_subtitles(self) -> List[Structable]:
        return self._subtitles


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

    def get_seasons(self) -> dict[int, SeasonMetadata]:
        return self._seasons
