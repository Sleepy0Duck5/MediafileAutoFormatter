from typing import List

from src.model.structable import Structable, extract_title


class Folder(Structable):
    def __init__(self, absolute_path: str) -> None:
        self._title = extract_title(absolute_path=absolute_path)
        self._absolute_path = absolute_path
        self._structs = []

    def get_title(self) -> str:
        return self._title

    def get_absolute_path(self) -> str:
        return self._absolute_path

    def append_struct(self, struct: Structable):
        self._structs.append(struct)

    def get_structs(self) -> List[Structable]:
        return self._structs
