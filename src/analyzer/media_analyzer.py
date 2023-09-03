from abc import ABCMeta
from typing import List
from loguru import logger

from src.model.folder import Folder
from src.model.metadata import Metadata, SeasonMetadata
from src.model.structable import Structable
from src.analyzer.metadata_builder import (
    MetadataBuilder,
    MovieMetadataBuilder,
    TVMetadataBuilder,
)
from src.constants import MediaType, FileType
from src.errors import MediaRootNotFoundException, MediaNotFoundException
from src.env_configs import EnvConfigs


# TODO: 하드코딩 제거, regex 적용 필요
def contains_season_suffix(str: str) -> bool:
    return ("시즌" in str) or ("Season" in str) or ("season" in str)


class MediaAnalyzer(metaclass=ABCMeta):
    def __init__(
        self,
        env_configs: EnvConfigs,
    ) -> None:
        raise NotImplementedError

    def analyze(self, root: Folder) -> Metadata:
        raise NotImplementedError


class GeneralMediaAnalyzer(MediaAnalyzer):
    def __init__(self, env_configs: EnvConfigs) -> None:
        self._env_configs = env_configs

    def _get_builder(self):
        raise NotImplementedError

    def analyze(self, root: Folder) -> Metadata:
        builder = self._get_builder()

        self._analyze(builder=builder, root=root)

        return builder.build()

    def _analyze(self, builder: MetadataBuilder, root: Folder) -> None:
        builder.set_root(root=root)
        builder.set_title(root.get_title())

        media_root = self._find_media_root(root=root)
        builder.set_media_root(media_root=media_root)
        builder.set_original_title(original_title=media_root.get_title())

    def _find_media_root(self, root: Folder) -> Folder:
        raise NotImplementedError

    # TODO: folder 내에 여러 자막이 있는 경우, 여러 파일 설정 필요
    def _get_subtitle_file(self, folder: Folder) -> List[Structable]:
        subtitles = []

        for file in folder.get_files():
            if file.get_file_type() in (
                FileType.SUBTITLE,
                FileType.ARCHIVED_SUBTITLE,
            ):
                subtitles.append(file)

        if len(subtitles) == 0:
            logger.warning(
                f"Subtitle must exists in {folder.get_absolute_path()}, but not found."
            )

        return subtitles

    def _analyze_subtitles(self, root: Folder) -> List[Structable]:
        if root.contains_subtitle_file():
            return self._get_subtitle_file(folder=root)

        for elem in root.get_structs():
            if isinstance(elem, Folder):
                if elem.contains_subtitle_file():
                    return self._get_subtitle_file(folder=elem)

        logger.info(f"Subtitle not found : {root.get_absolute_path()}")
        return []


class MovieAnalyzer(GeneralMediaAnalyzer):
    def __init__(self, env_configs: EnvConfigs) -> None:
        super().__init__(env_configs)
        self._media_type = MediaType.MOVIE

    def _get_builder(self):
        return MovieMetadataBuilder(self._media_type)

    def _analyze(self, builder: MovieMetadataBuilder, root: Folder) -> None:
        super()._analyze(builder, root)

        subtitles = self._analyze_subtitles(root=root)
        builder.set_subtitles(subtitles=subtitles)

    def _find_media_root(self, root: Folder) -> Folder:
        if root.get_number_of_files_by_type(file_type=FileType.MEDIA) > 0:
            return root

        for folder in root.get_folders():
            if folder.get_number_of_files_by_type(file_type=FileType.MEDIA) > 0:
                return folder

        raise MediaRootNotFoundException


class TVAnalyzer(GeneralMediaAnalyzer):
    def __init__(self, env_configs: EnvConfigs) -> None:
        super().__init__(env_configs)
        self._media_type = MediaType.TV

    def _get_builder(self):
        return TVMetadataBuilder()

    def _analyze(self, builder: TVMetadataBuilder, root: Folder) -> None:
        super()._analyze(builder, root)

        seasons = self._analyze_season(
            builder=builder, media_root=builder.get_media_root(), root=root
        )
        builder.set_seasons(seasons=seasons)

    def _find_media_root(self, root: Folder) -> Folder:
        media_contained_folder = []

        for folder in root.get_folders():
            if folder.get_number_of_files_by_type(file_type=FileType.MEDIA) > 0 or (
                contains_season_suffix(folder.get_title())
            ):
                media_contained_folder.append(folder)

        if len(media_contained_folder) == 1:
            return media_contained_folder[0]

        return root

    def _analyze_season(
        self, builder: TVMetadataBuilder, media_root: Folder, root: Folder
    ) -> dict[int, SeasonMetadata]:
        seasons = {}

        folders = media_root.get_structs()
        folders.sort(key=lambda struct: struct.get_title())

        season_index = 1
        for folder in media_root.get_folders():
            season_title = folder.get_title()

            if contains_season_suffix(str=season_title):
                subtitles = self._analyze_subtitles(root=folder)

                seasons[season_index] = SeasonMetadata(
                    title=builder.get_title(),
                    original_title=season_title,
                    root=media_root,
                    media_root=folder,
                    subtitles=subtitles,
                )
                season_index += 1

        if not seasons:
            if media_root.get_number_of_files_by_type(FileType.MEDIA) <= 0:
                raise MediaNotFoundException("TV media found but no seasons")

            subtitles = self._analyze_subtitles(root=root)

            seasons[season_index] = SeasonMetadata(
                title=builder.get_title(),
                original_title=media_root.get_title(),
                root=root,
                media_root=media_root,
                subtitles=subtitles,
            )

        return seasons
