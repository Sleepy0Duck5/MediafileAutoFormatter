from abc import ABCMeta
from loguru import logger

from src.model.folder import Folder
from src.analyzer.metadata_reader import MetadataReader
from src.constants import Constants, Extensions, MediaType, FileType
from src.env_configs import EnvConfigs
from src.analyzer.error import MediaNotFoundException
from src.errors import AbortException


def _is_user_define_metadata_included(root: Folder) -> bool:
    for file in root.get_files():
        if file.get_extension() == Extensions.TXT and (
            file.get_title() == Constants.METADATA_FILENAME
        ):
            return True
    return False


def _is_error_log_included(root: Folder) -> bool:
    for file in root.get_files():
        if file.get_extension() == Extensions.LOG and (
            file.get_title() == Constants.ERROR_LOG_FILENAME
        ):
            return True
    return False


class MediaTypeAnalyzer(metaclass=ABCMeta):
    def __init__(
        self, env_configs: EnvConfigs, metadata_reader: MetadataReader
    ) -> None:
        self._env_configs = env_configs
        self._metadata_reader = metadata_reader

    def analyze(self, root: Folder) -> MediaType:
        raise NotImplementedError


class GeneralMediaTypeAnalyzer(MediaTypeAnalyzer):
    def analyze(self, root: Folder) -> MediaType:
        if _is_user_define_metadata_included(root=root):
            raise NotImplementedError("User define metadata not work yet.")

        if _is_error_log_included(root=root):
            raise AbortException("Error log file already exists! Aborting...")

        return self._analyze_media_type(root=root)

    def _analyze_media_type(self, root: Folder) -> MediaType:
        total_count_of_media_file = self._count_media_files_recursively(root=root)

        if total_count_of_media_file <= 0:
            logger.warning(f"No media file found in {root.get_absolute_path()}")

        if total_count_of_media_file == 1:
            return MediaType.MOVIE

        return MediaType.TV

    def _count_media_files_recursively(self, root: Folder) -> int:
        media_file_count = root.get_number_of_files_by_type(file_type=FileType.MEDIA)

        for folder in root.get_folders():
            media_file_count += self._count_media_files_recursively(folder)

        return media_file_count
