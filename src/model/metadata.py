from abc import ABCMeta
from typing import Optional, List

from src.constants import MediaType
from src.model.file import File
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

    def explain(self) -> str:
        return f"""<Metadata>
Title : {self.get_title()}
OriginalTitle : {self.get_original_title()}
MediaType : {self.get_media_type()}
MediaRoot : {self.get_media_root().get_absolute_path()}
"""


class SubtitleContainingMetadata(Metadata):
    def __init__(
        self,
        title: str,
        original_title: str,
        media_type: MediaType,
        root: Folder,
        media_root: Folder,
        media_files: List[File],
        subtitles: List[Structable],
    ) -> None:
        super().__init__(title, original_title, media_type, root, media_root)
        self._media_files = media_files
        self._subtitles = subtitles

    def get_media_files(self) -> List[File]:
        return self._media_files

    def get_subtitles(self) -> List[Structable]:
        return self._subtitles


class MovieMetadata(SubtitleContainingMetadata):
    def __init__(
        self,
        title: str,
        original_title: str,
        root: Folder,
        media_root: Folder,
        media_files: List[File],
        subtitles: List[Structable],
    ) -> None:
        super().__init__(
            title,
            original_title,
            MediaType.MOVIE,
            root,
            media_root,
            media_files,
            subtitles,
        )


class SeasonMetadata(SubtitleContainingMetadata):
    def __init__(
        self,
        title: str,
        original_title: str,
        root: Folder,
        media_root: Folder,
        media_files: List[File],
        subtitles: List[Structable],
        season_index: int,
        episode_files: dict[int, File],
    ) -> None:
        super().__init__(
            title,
            original_title,
            MediaType.TV,
            root,
            media_root,
            media_files,
            subtitles,
        )
        self._season_index = season_index
        self._episode_files = episode_files

    def get_season_index(self) -> int:
        return self._season_index

    def get_episode_files(self) -> dict[int, File]:
        return self._episode_files

    def explain(self) -> str:
        return """<Season>
SeasonIndex : {self._season_index}
Episodes : {len(self._episode_files.keys())}
"""


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
