import os
from abc import ABCMeta

from src.model.folder import Folder
from src.model.metadata import Metadata
from src.formatter.formatter import Formatter
from src.env_configs import EnvConfigs
from src.errors import TargetPathNotFoundException


class Restructor(metaclass=ABCMeta):
    def __init__(self, env_configs: EnvConfigs, formatter: Formatter) -> None:
        raise NotImplementedError

    def restruct(self, metadata: Metadata, target_path: str) -> Folder:
        raise NotImplementedError


class GeneralRestructor(Restructor):
    def __init__(self, env_configs: EnvConfigs, formatter: Formatter) -> None:
        self._env_configs = env_configs
        self._formatter = formatter

    def restruct(self, metadata: Metadata, target_path: str) -> Folder:
        raise NotImplementedError


class MovieRestructor(GeneralRestructor):
    def restruct(self, metadata: Metadata, target_path: str) -> Folder:
        if not os.path.exists(path=target_path):
            raise TargetPathNotFoundException

        # TODO: 폴더명 리포맷 필요(특수문자 제거)
        root_folder_title = self._formatter.format_folder_name(
            folder_name=metadata.get_title()
        )
        new_root_absoluth_path = os.path.join(target_path, root_folder_title)

        new_root_folder = Folder(absolute_path=metadata.get_root().get_absolute_path())
        raise NotImplementedError


class TVRestructor(GeneralRestructor):
    pass
