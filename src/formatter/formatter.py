import re, os

from abc import ABCMeta
from src.env_configs import EnvConfigs


class Formatter(metaclass=ABCMeta):
    def __init__(self, env_configs: EnvConfigs) -> None:
        raise NotImplementedError

    def format_folder_name(self, folder_name: str) -> str:
        raise NotImplementedError


class GeneralFormatter(Formatter):
    def __init__(self, env_configs: EnvConfigs) -> None:
        self._env_configs = env_configs

    def format_folder_name(self, folder_name: str) -> str:
        # TODO: 특수기호 제외 regex
        return folder_name
