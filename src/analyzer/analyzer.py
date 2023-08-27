from abc import ABCMeta
from typing import Optional

from src.model.folder import Folder
from src.model.file import File
from src.model.metadata import Metadata
from src.model.structable import Structable
from src.analyzer.metadata_reader import MetadataReader
from src.analyzer.metadata_builder import MetadataBuilder
from src.constants import Constants, Extensions, MediaType, FileType
from src.errors import MediaRootNotFoundException
from src.env_configs import EnvConfigs


def _is_metadata_included(root: Folder) -> bool:
    for elem in root.get_structs():
        if isinstance(elem, File):
            if elem.get_extension() == Extensions.TXT and (
                elem.get_title() == Constants.METADATA_FILENAME
            ):
                return True
    return False


class Analyzer(metaclass=ABCMeta):
    def __init__(
        self, env_configs: EnvConfigs, metadata_reader: MetadataReader
    ) -> None:
        self._env_configs = env_configs
        self._metadata_reader = metadata_reader

    def analyze(self, root: Folder) -> Metadata:
        raise NotImplementedError


class GeneralAnalyzer(Analyzer):
    def analyze(self, root: Folder) -> Metadata:
        if _is_metadata_included(root=root):
            # return self._metadata_reader.read()
            raise NotImplementedError

        builder = MetadataBuilder()

        builder.set_title(root.get_title())
        builder.set_root_path(root_path=root.get_absolute_path())

        media_root = self._analyze_media_root(root=root)
        builder.set_media_root(media_root=media_root)
        builder.set_original_title(original_title=media_root.get_title())

        seasons = self._analyze_seasons(media_root=media_root)
        builder.set_seasons(seasons=seasons)

        media_type = self._analyze_media_type(media_root=media_root, seasons=seasons)
        builder.set_media_type(media_type=media_type)

        subtitles = self._analyze_subtitles(
            root=root, seasons=seasons, media_type=media_type
        )
        builder.set_subtitles(subtitles=subtitles)

        return builder.build()

    def _analyze_media_root(self, root: Folder) -> Folder:
        # TODO: 더 확실하게 찾는 방법으로 수정 필요 (Media file 갯수 확인 등)
        for elem in root.get_structs():
            if isinstance(elem, Folder):
                return elem

        raise MediaRootNotFoundException()

    def _analyze_seasons(self, media_root: Folder) -> dict[str, Folder]:
        seasons = {}

        # TODO: regex 적용 필요, 정렬 필요
        for elem in media_root.get_structs():
            if isinstance(elem, Folder):
                title = elem.get_title()
                if "시즌" in title:
                    seasons[title] = elem

        return seasons

    def _analyze_media_type(
        self, media_root: Folder, seasons: dict[str, Folder]
    ) -> MediaType:
        if len(seasons) > 0:
            return MediaType.TV

        media_count = 0

        for elem in media_root.get_structs():
            if isinstance(elem, File) and elem.get_file_type() == FileType.MEDIA:
                media_count += 1

        if media_count == 1:
            return MediaType.MOVIE

        return MediaType.TV

    def _search_and_analyze(
        self,
        root: Folder,
    ) -> Optional[Structable]:
        for elem in root.get_structs():
            if isinstance(elem, File):
                if elem.get_file_type() in (
                    FileType.SUBTITLE,
                    FileType.ARCHIVED_SUBTITLE,
                ):
                    return elem

        return None

    # TODO: 반환형에 대한 고민이 필요
    def _analyze_subtitles(
        self, root: Folder, seasons: dict[str, Folder], media_type: MediaType
    ) -> Optional[dict[str, Structable]]:
        if (media_type == MediaType.MOVIE) or (
            media_type == MediaType.TV and len(seasons) <= 0
        ):
            subtitles = self._search_and_analyze(root=root)
            if subtitles:
                return {Constants.UNKNOWN: subtitles}
            return None

        if media_type == MediaType.TV:
            subtitles = {}
            for season in seasons:
                subtitles[season] = self._search_and_analyze(root=seasons[season])

            return subtitles

        raise NotImplementedError
