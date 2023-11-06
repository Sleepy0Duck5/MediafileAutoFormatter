import os
import shutil
from abc import ABCMeta
from loguru import logger

from src.model.folder import RestructedFolder
from src.model.file import RestructedFile
from src.model.metadata import Metadata
from src.executor.errors import FailedToCreateDirectoryException
from src.errors import DirectoryNotFoundException
from src.log_exporter import LogExporter


class Executor(metaclass=ABCMeta):
    def __init__(self, log_exporter: LogExporter) -> None:
        raise NotImplementedError

    def execute(self, new_root_folder: RestructedFolder, metadata: Metadata) -> None:
        raise NotImplementedError


class GeneralExecutor(Executor):
    def __init__(self, log_exporter: LogExporter) -> None:
        self._log_exporter = log_exporter

    def execute(self, new_root_folder: RestructedFolder, metadata: Metadata) -> None:
        self._execute(
            folder=new_root_folder,
            absolute_path=new_root_folder.get_absolute_path(),
        )

        backup_path = os.path.join(
            os.path.join(new_root_folder.get_absolute_path(), "MAF_Backup"),
            metadata.get_root().get_title(),
        )
        self._move_directory(
            src_path=metadata.get_root().get_absolute_path(),
            target_path=backup_path,
        )

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
            raise FailedToCreateDirectoryException(
                f"Failed to create directory : Directory already exists! {new_directory_path}"
            )

        os.mkdir(new_directory_path)
        self._append_log(f"New directory created {new_directory_path}")

        return new_directory_path

    def _move_file(self, file: RestructedFile) -> None:
        try:
            src_path = file.get_original_file().get_absolute_path()

            if not os.path.exists(src_path):
                raise FileNotFoundError(
                    f"Move file failed : File not found in {src_path}"
                )

            target_path = file.get_absolute_path()
            if os.path.exists(target_path):
                raise FileExistsError(
                    f"Move file failed : File already exists in {target_path}"
                )

            os.rename(src_path, target_path)
            self._append_log(f"File moved successfuly : {src_path} -> {target_path}")
        except Exception as e:
            raise e

    def _move_directory(self, src_path: str, target_path: str) -> None:
        try:
            if not os.path.exists(src_path):
                raise DirectoryNotFoundException(
                    f"Move directory failed : Directory not found in {src_path}"
                )

            if os.path.exists(target_path):
                raise FileExistsError(
                    f"Move directory failed : Directory already exists in {target_path}"
                )

            shutil.move(src=src_path, dst=target_path)
            self._append_log(
                f"Directory moved successfuly : {src_path} -> {target_path}"
            )
        except Exception as e:
            raise e

    def _append_log(self, message: str):
        logger.info(message)
        self._log_exporter.append_log(message + "\n")
