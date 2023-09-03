import os
from typing import Optional

from src.model.structable import Structable
from src.constants import FileType


def extract_extension(absolute_path: str) -> str:
    return absolute_path.split(".")[-1]


class File(Structable):
    def __init__(self, absolute_path: str, file_type: FileType) -> None:
        self._title = self._extract_title(absolute_path=absolute_path)
        self._absolute_path = absolute_path
        self._extension = extract_extension(absolute_path=absolute_path)
        self._file_type = file_type

    def _extract_title(self, absolute_path: str) -> str:
        file_full_name = absolute_path.split(sep=os.sep)[-1]
        return file_full_name.rsplit(sep=".", maxsplit=1)[0]

    def get_title(self) -> str:
        return self._title

    def get_absolute_path(self) -> str:
        return self._absolute_path

    def get_extension(self) -> str:
        return self._extension

    def get_file_type(self) -> FileType:
        return self._file_type


class RestructedFile(File):
    def __init__(
        self, absolute_path: str, file_type: FileType, original_file: File
    ) -> None:
        super().__init__(absolute_path, file_type)
        self._original_file = original_file
