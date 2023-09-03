import os
from abc import ABCMeta
from patoolib import test_archive
from loguru import logger

from src.model.file import File, extract_extension
from src.model.folder import Folder
from src.env_configs import EnvConfigs
from src.constants import FileType, Extensions


def _is_archived_subtitle(absolute_path: str):
    try:
        test_archive(absolute_path, verbosity=-1)
        return True
    except Exception as e:
        logger.warning(e)
        return False


class Constructor(metaclass=ABCMeta):
    def __init__(self, env_configs: EnvConfigs) -> None:
        raise NotImplementedError

    def struct(self, source_path: str) -> Folder:
        raise NotImplementedError


class GeneralConstructor(Constructor):
    def __init__(self, env_configs: EnvConfigs) -> None:
        self._env_confg = env_configs

    def struct(self, source_path: str) -> Folder:
        try:
            return self._search_and_struct(path=source_path)
        except FileNotFoundError as e:
            raise e

    def _get_file_type(self, absolute_path: str) -> FileType:
        extension = extract_extension(absolute_path=absolute_path)

        if extension in (self._env_confg._MEDIA_EXTENSIONS):
            return FileType.MEDIA

        if extension in (self._env_confg._SUBTITLE_EXTENSIONS):
            return FileType.SUBTITLE

        if extension == Extensions.NFO:
            return FileType.NFO

        if _is_archived_subtitle(absolute_path=absolute_path):
            return FileType.ARCHIVED_SUBTITLE

        return FileType.EXTRA

    def _search_and_struct(self, path: str) -> Folder:
        folder = Folder(absolute_path=path)

        for elem_name in os.listdir(path=path):
            elem_absolute_path = os.path.join(folder.get_absolute_path(), elem_name)

            if os.path.isdir(elem_absolute_path):
                folder.append_struct(self._search_and_struct(path=elem_absolute_path))
                continue

            file_type = self._get_file_type(absolute_path=elem_absolute_path)
            folder.append_struct(
                File(absolute_path=elem_absolute_path, file_type=file_type)
            )

        return folder
