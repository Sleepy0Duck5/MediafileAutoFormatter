import os
from abc import ABCMeta
from loguru import logger

from src.model.folder import RestructedFolder
from src.model.file import RestructedFile
from src.model.metadata import Metadata
from src.executor.errors import FailedToCreateDirectoryException


class Executor(metaclass=ABCMeta):
    def __init__(self) -> None:
        pass

    def execute(self, new_root_folder: RestructedFolder, metadata: Metadata) -> None:
        pass


class GeneralExecutor(Executor):
    def execute(self, new_root_folder: RestructedFolder, metadata: Metadata) -> None:
        try:
            self._execute(
                folder=new_root_folder,
                absolute_path=new_root_folder.get_absolute_path(),
            )
        except Exception as e:
            logger.info(e)

    def _execute(self, folder: RestructedFolder, absolute_path: str) -> None:
        new_directory_path = self._create_directory(
            folder=folder, absolute_path=absolute_path
        )

        for child_folder in folder.get_folders():
            self._execute(folder=child_folder, absolute_path=new_directory_path)

        for file in folder.get_files():
            if isinstance(file, RestructedFile):
                self._move_file(file=file)

    def _create_directory(self, folder: RestructedFolder, absolute_path: str) -> str:
        new_directory_path = os.path.join(absolute_path, folder.get_title())

        if absolute_path == folder.get_absolute_path():
            new_directory_path = folder.get_absolute_path()

        if os.path.exists(new_directory_path):
            raise FailedToCreateDirectoryException("New root folder already exists!")

        os.mkdir(new_directory_path)
        logger.info(f"New directory created {new_directory_path}")

        return new_directory_path

    def _move_file(self, file: RestructedFile) -> None:
        try:
            src = file.get_original_file().get_absolute_path()
            if not os.path.exists(src):
                raise FileNotFoundError(f"move_file failed : file not found in {src}")

            target = file.get_absolute_path()
            if os.path.exists(target):
                raise FileExistsError(
                    f"move_file failed : file already exists in {target}"
                )

            os.rename(src, target)
            logger.info(f"File moved successfuly : {src} -> {target}")
        except Exception as e:
            raise e
