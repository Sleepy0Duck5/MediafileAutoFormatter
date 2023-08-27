from abc import ABCMeta


class Restructor(metaclass=ABCMeta):
    def restruct(self, source_path: str, target_path: str):
        raise NotImplementedError
