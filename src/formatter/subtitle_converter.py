from abc import ABCMeta
from typing import List

from src.model.file import File
from src.env_configs import EnvConfigs


class SubtitleConverter(metaclass=ABCMeta):
    def __init__(self, env_configs: EnvConfigs) -> None:
        self._env_configs = env_configs

    def convert_subtitle(self, file: File) -> List[File]:
        raise NotImplementedError
