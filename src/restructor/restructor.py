from abc import ABCMeta


from src.model.folder import Folder
from src.model.metadata import Metadata


class Restructor(metaclass=ABCMeta):
    def restruct(self, root: Folder, metadata: Metadata) -> Folder:
        raise NotImplementedError


class GeneralRestructor(Restructor):
    def restruct(self, root: Folder, metadata: Metadata) -> Folder:
        raise NotImplementedError
