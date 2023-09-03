import re

from abc import ABCMeta
from src.env_configs import EnvConfigs
from src.errors import InvalidFolderNameException


class Formatter(metaclass=ABCMeta):
    def __init__(self, env_configs: EnvConfigs) -> None:
        raise NotImplementedError

    def format_folder_name(self, folder_name: str) -> str:
        raise NotImplementedError


class GeneralFormatter(Formatter):
    def __init__(self, env_configs: EnvConfigs) -> None:
        self._env_configs = env_configs

    def format_folder_name(self, folder_name: str) -> str:
        pattern = re.compile('[*\\￦|¦:"/?]')
        replaced = pattern.sub(repl=" ", string=folder_name).strip()

        if len(replaced) <= 0:
            raise InvalidFolderNameException

        return replaced
