from abc import ABCMeta

from src.model.folder import Folder


class Executor(metaclass=ABCMeta):
    def execute(self, result_folder: Folder):
        pass


class GeneralExecutor(Executor):
    def execute(self, result_folder: Folder):
        pass
