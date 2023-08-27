from abc import ABCMeta

from src.model.folder import Folder


class Executor(metaclass=ABCMeta):
    def save(self, result_folder: Folder):
        pass


class GeneralExecutor(Executor):
    def save(self, result_folder: Folder):
        pass
