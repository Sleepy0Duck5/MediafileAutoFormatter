import re
from abc import ABCMeta

from src.env_configs import EnvConfigs
from src.model.metadata import Metadata, SeasonMetadata
from src.formatter.errors import InvalidFolderNameException
from src.errors import InvalidMediaTypeException
from src.constants import Constants, MediaType, FileType
from src.model.file import File


class Formatter(metaclass=ABCMeta):
    def __init__(self, env_configs: EnvConfigs) -> None:
        raise NotImplementedError

    def format_name(self, name: str) -> str:
        raise NotImplementedError

    def rename_file(self, metadata: Metadata, file: File, **kwargs) -> str:
        raise NotImplementedError

    def rename_subtitle_file(self, metadata: Metadata, subtitle_file: File) -> str:
        raise NotImplementedError


class GeneralFormatter(Formatter):
    def __init__(self, env_configs: EnvConfigs) -> None:
        self._env_configs = env_configs

    def format_name(self, name: str) -> str:
        pattern = re.compile('[*\\￦|¦:"/?]')
        replaced = pattern.sub(repl=" ", string=name).strip()

        if len(replaced) <= 0:
            raise InvalidFolderNameException

        return replaced[: Constants.MAXIMUM_FOLDER_NAME_LENGTH]

    def rename_subtitle_file(self, metadata: Metadata, subtitle_file: File) -> str:
        new_file_name = (
            metadata.get_title()
            + "."
            + self._env_configs._SUBTITLE_SUFFIX
            + "."
            + subtitle_file.get_extension()
        )
        return self.format_name(new_file_name)


class MovieFormatter(GeneralFormatter):
    def rename_file(self, metadata: Metadata, file: File) -> str:
        return self.format_name(metadata.get_title())


class TVFormatter(GeneralFormatter):
    def rename_file(
        self, metadata: SeasonMetadata, file: File, episode_index: int
    ) -> str:
        replace_strings = {
            "title": metadata.get_title(),
            "season_number": str(metadata.get_season_index()).zfill(
                self._env_configs._SEASON_NUMBER_DIGIT
            ),
            "episode_number": str(episode_index).zfill(
                self._env_configs._EPISODE_NUMBER_DIGIT
            ),
        }

        new_file_name = ""
        pattern = re.compile("{{\\s*\\w+\\s*}}")
        cursor = 0

        for iter in pattern.finditer(self._env_configs._FILENAME_FORMAT):
            new_file_name += self._env_configs._FILENAME_FORMAT[cursor : iter.start()]

            for replace_string in replace_strings:
                if replace_string in iter.group():
                    new_file_name += replace_strings.get(replace_string, "")
                    break

            cursor = iter.end()

        if file.get_file_type() == FileType.SUBTITLE:
            new_file_name += "." + self._env_configs._SUBTITLE_SUFFIX

        return self.format_name(new_file_name)
