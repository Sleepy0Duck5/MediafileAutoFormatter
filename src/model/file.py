from typing import Optional

from src.model.structable import Structable, extract_title
from src.constants import FileType


def extract_extension(absolute_path: str) -> str:
    return absolute_path.split(".")[-1]


class File(Structable):
    def __init__(self, absolute_path: str, file_type: FileType) -> None:
        self._title = extract_title(absolute_path=absolute_path)
        self._absolute_path = absolute_path
        self._extension = extract_extension(absolute_path=absolute_path)
        self._file_type = file_type

    def get_title(self) -> str:
        return self._title

    def get_absolute_path(self) -> str:
        return self._absolute_path

    def get_extension(self) -> str:
        return self._extension

    def get_file_type(self) -> FileType:
        return self._file_type
