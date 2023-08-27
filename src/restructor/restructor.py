from abc import ABCMeta

from src.model.file import File
from src.model.folder import Folder


def _is_metadata_included(root: Folder) -> bool:
    for elem in root.get_structs():
        if isinstance(elem, File):
            if elem.get_extension() == "txt" and (elem.get_title() == "metadata"):
                return True
    return False


class Restructor(metaclass=ABCMeta):
    def restruct(self, source_path: str, target_path: str):
        raise NotImplementedError
