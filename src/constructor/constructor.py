import os
from abc import ABCMeta
from typing import List

from src.model.structable import Structable
from src.model.file import File
from src.model.folder import Folder


class Constructor(metaclass=ABCMeta):
    def struct(self, source_path: str) -> List[Structable]:
        raise NotImplementedError


class GeneralConstructor(Constructor):
    def struct(self, source_path: str) -> List[Structable]:
        return self._search_and_struct(path=source_path)

    def _search_and_struct(self, path: str) -> List[Structable]:
        folder = Folder(absolute_path=path)

        for elem_name in os.listdir(path=path):
            elem_absolute_path = os.path.join(folder.get_absolute_path(), elem_name)

            if os.path.isdir(elem_absolute_path):
                folder.append_struct(self._search_and_struct(path=elem_absolute_path))
                continue

            folder.append_struct(File(absolute_path=elem_absolute_path))

        return folder
