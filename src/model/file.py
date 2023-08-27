import os

from src.model.structable import Structable, extract_title


def _extract_extension(absolute_path: str) -> str:
    return absolute_path.split(".")[-1]


class File(Structable):
    def __init__(self, absolute_path: str) -> None:
        self._title = extract_title(absolute_path=absolute_path)
        self._absolute_path = absolute_path
        self._extension = _extract_extension(absolute_path=absolute_path)

    def get_title(self) -> str:
        return self._title

    def get_absolute_path(self) -> str:
        return self._absolute_path

    def get_extension(self) -> str:
        return self._extension
