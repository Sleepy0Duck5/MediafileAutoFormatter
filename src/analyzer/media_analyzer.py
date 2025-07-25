import re
import itertools
from abc import ABCMeta
from typing import List, Optional
from loguru import logger

from src.model.file import File
from src.model.folder import Folder
from src.model.metadata import Metadata, SeasonMetadata
from src.model.structable import Structable
from src.analyzer.metadata_builder import (
    MetadataBuilder,
    MovieMetadataBuilder,
    TVMetadataBuilder,
)
from src.analyzer.error import (
    MediaRootNotFoundException,
    EpisodeIndexNotFoundException,
    EpisodeIndexDuplicatedException,
    SeasonIndexNotFoundException,
)
from src.analyzer.mkv_subtitle_extractor import MkvSubtitleExtractor
from src.constants import MediaType, FileType, SeasonAlias
from src.env_configs import EnvConfigs


# TODO: regex 적용 필요
def find_season_keyword(str: str) -> Optional[str]:
    for alias in SeasonAlias.SEASON_ALIASES:
        if alias in str.lower():
            return alias
    return None


def _extract_season_number_from_string(str: str, season_keyword: str) -> Optional[int]:
    for i in re.finditer(rf"{season_keyword}.?[0-9]+", str.lower()):
        str_index = i.group().replace(season_keyword, "").strip()
        if str_index.isnumeric():
            return int(str_index)

    return None


def extract_season_index(folder_name: str) -> Optional[int]:
    season_keyword = find_season_keyword(str=folder_name)
    if not season_keyword:
        return None
    return _extract_season_number_from_string(
        str=folder_name, season_keyword=season_keyword
    )


def replace_special_chars(str: str) -> str:
    underscore_replaced = str.replace("_", " ")
    dot_replaced = underscore_replaced.replace(".", " ")
    return dot_replaced


class MediaAnalyzer(metaclass=ABCMeta):
    def __init__(
        self, env_configs: EnvConfigs, mkv_subtitle_extractor: MkvSubtitleExtractor
    ) -> None:
        raise NotImplementedError

    def analyze(self, root: Folder) -> Metadata:
        raise NotImplementedError


class GeneralMediaAnalyzer(MediaAnalyzer):
    def __init__(
        self, env_configs: EnvConfigs, mkv_subtitle_extractor: MkvSubtitleExtractor
    ) -> None:
        self._env_configs = env_configs
        self._mkv_subtitle_extractor = mkv_subtitle_extractor

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

    def _get_media_files(self, root: Folder) -> List[File]:
        media_files = []
        for file in root.get_files():
            if file.get_file_type() == FileType.MEDIA:
                media_files.append(file)

        if not media_files:
            for child in root.get_folders():
                media_files.extend(self._get_media_files(child))

        return media_files

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
    def __init__(
        self, env_configs: EnvConfigs, mkv_subtitle_extractor: MkvSubtitleExtractor
    ) -> None:
        super().__init__(env_configs, mkv_subtitle_extractor)
        self._media_type = MediaType.MOVIE

    def _get_builder(self):
        return MovieMetadataBuilder(self._media_type)

    def _analyze(self, builder: MovieMetadataBuilder, root: Folder) -> None:
        super()._analyze(builder, root)

        subtitles = self._analyze_subtitles(root=root)

        media_files = self._get_media_files(root=builder.get_media_root())
        builder.set_media_files(media_files=media_files)

        subtitles = self._mkv_subtitle_extractor.extract_subtitle_file_from_mkv(
            media_files=media_files, subtitles=subtitles
        )
        builder.set_subtitles(subtitles=subtitles)

    def _find_media_root(self, root: Folder) -> Folder:
        if root.get_number_of_files_by_type(file_type=FileType.MEDIA) > 0:
            return root

        for folder in root.get_folders():
            if folder.get_number_of_files_by_type(file_type=FileType.MEDIA) > 0:
                return folder

        raise MediaRootNotFoundException


class TVAnalyzer(GeneralMediaAnalyzer):
    def __init__(
        self, env_configs: EnvConfigs, mkv_subtitle_extractor: MkvSubtitleExtractor
    ) -> None:
        super().__init__(env_configs, mkv_subtitle_extractor)
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
                find_season_keyword(folder.get_title())
            ):
                media_contained_folder.append(folder)

        if len(media_contained_folder) == 1:
            return media_contained_folder[0]

        return root

    def _find_season_folders(self, root: Folder) -> List[Folder]:
        season_folders = []

        for folder in root.get_folders():
            if find_season_keyword(folder.get_title()):
                season_folders.append(folder)

        return season_folders

    def _analyze_season(
        self, builder: TVMetadataBuilder, media_root: Folder, root: Folder
    ) -> dict[int, SeasonMetadata]:
        seasons = {}

        season_folders = self._find_season_folders(root=root)

        # season folder not found
        if not season_folders:
            # try to extract season index, if none then set as first season
            season_index = extract_season_index(folder_name=media_root.get_title())
            if not season_index:
                season_index = 1

            seasons[season_index] = self._get_season_metadata(
                builder=builder,
                media_root=media_root,
                root=root,
                season_index=season_index,
            )
            return seasons

        for season_root in season_folders:
            season_title = season_root.get_title()
            season_index = extract_season_index(folder_name=season_title)

            if season_index is None:
                if len(media_root.get_folders()) > 1:
                    raise SeasonIndexNotFoundException(
                        "Failed to detect season index from season folder name, but multiple season folder exists. Try to rename season foler name."
                    )
                season_index = 1

            season_media_root = self._find_media_root(root=season_root)
            seasons[season_index] = self._get_season_metadata(
                builder=builder,
                media_root=season_root,
                root=season_media_root,
                season_index=season_index,
            )

        return seasons

    def _get_episodes(self, media_files: List[File]) -> dict[int, File]:
        episodes = {}

        sorted(media_files, key=lambda file: file.get_title())

        episode_index_not_found_files = []

        file_name_prefix = self._get_file_name_prefix(files=media_files)

        for media_file in media_files:
            file_title = media_file.get_title()

            try:
                episode_index = self._extract_episode_index_from_file_name(
                    file_name=file_title, prefix=file_name_prefix
                )
            except EpisodeIndexNotFoundException:
                logger.info(f"Episode index not found from {file_title}")
                episode_index_not_found_files.append(media_file)
                continue

            if episodes.get(episode_index, None):
                logger.info(f"Duplicated episode index found from {file_title}")
                episode_index_not_found_files.append(media_file)
                continue

            if episodes.get(episode_index):
                raise EpisodeIndexDuplicatedException("Duplicated episode index found")

            episodes[episode_index] = media_file

        return episodes

    def _get_file_name_prefix(self, files: List[File]) -> str:
        file_names = [file.get_title() for file in files]
        if len(file_names) <= 1:
            return ""

        res = "".join(
            c[0]
            for c in itertools.takewhile(
                lambda x: all(x[0] == y for y in x), zip(*file_names)
            )
        )

        if not res:
            logger.warning(f"Failed to found file prefix from file name")
        return res

    def _extract_episode_index_from_file_name(self, file_name: str, prefix: str) -> int:
        prefix_removed = file_name.replace(prefix, "")

        # try to split by episode spliter
        index = self._extract_episode_index_from_normalized_form(str=prefix_removed)
        if index:
            return index

        for numeric_span in re.finditer(r"\d+", prefix_removed):
            str_index = numeric_span.group()

            if str_index.isnumeric():
                return int(str_index)

        raise EpisodeIndexNotFoundException

    def _extract_episode_index_from_normalized_form(self, str: str) -> Optional[int]:
        try:
            for i in re.finditer(r"S[0-9]+E[0-9]+", str):
                str_episode = i.group()
                splited = str_episode.split("E")[1]

                if splited.isnumeric():
                    return int(splited)

        except Exception as e:
            logger.warning(
                f"Failed to extract episode index from normalized form (format : S00E00) : {e}"
            )

        return None

    def _get_season_metadata(
        self,
        builder: TVMetadataBuilder,
        media_root: Folder,
        root: Folder,
        season_index: int,
    ) -> SeasonMetadata:
        subtitles = self._analyze_subtitles(root=root)
        media_files = self._get_media_files(root=root)
        subtitles = self._mkv_subtitle_extractor.extract_subtitle_file_from_mkv(
            media_files=media_files, subtitles=subtitles
        )

        return SeasonMetadata(
            title=builder.get_title(),
            original_title=media_root.get_title(),
            root=root,
            media_root=media_root,
            media_files=media_files,
            subtitles=subtitles,
            season_index=season_index,
            episode_files=self._get_episodes(media_files),
        )
