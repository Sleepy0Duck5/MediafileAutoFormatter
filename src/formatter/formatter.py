import re
from abc import ABCMeta

from src.env_configs import EnvConfigs
from src.model.metadata import Metadata, SeasonMetadata
from src.errors import InvalidFolderNameException, InvalidMediaTypeException
from src.constants import Constants, MediaType


class Formatter(metaclass=ABCMeta):
    def __init__(self, env_configs: EnvConfigs) -> None:
        raise NotImplementedError

    def _format_name(self, name: str) -> str:
        raise NotImplementedError

    def format_mediafile_name(self, name: str, metadata: Metadata) -> str:
        raise NotImplementedError

    def format_folder_name(self, name: str, metadata: Metadata) -> str:
        raise NotImplementedError


class GeneralFormatter(Formatter):
    def __init__(self, env_configs: EnvConfigs) -> None:
        self._env_configs = env_configs

    def _format_name(self, name: str) -> str:
        pattern = re.compile('[*\\￦|¦:"/?]')
        replaced = pattern.sub(repl=" ", string=name).strip()

        if len(replaced) <= 0:
            raise InvalidFolderNameException

        return replaced[: Constants.MAXIMUM_FOLDER_NAME_LENGTH]

    def _format_index(self, index: int) -> str:
        return str(index).zfill(Constants.FILENAME_INDEX_ZFILL)

    def _extract_index_from_filename(self, filename: str) -> int:
        raise NotImplementedError

    def format_mediafile_name(self, filename: str, metadata: Metadata) -> str:
        if metadata.get_media_type() == MediaType.MOVIE:
            return self._format_name(metadata.get_title())

        if metadata.get_media_type() == MediaType.TV:
            if isinstance(metadata, SeasonMetadata):
                season_index = self._format_index(index=metadata.get_season_index())

                episode_index = self._format_index(
                    index=self._extract_index_from_filename(filename=filename)
                )

                title = f"{metadata.get_title()} - S{season_index}E{episode_index}"

                return self._format_name(title)

        raise InvalidMediaTypeException

    def format_folder_name(self, name: str, metadata: Metadata) -> str:
        raise NotImplementedError
