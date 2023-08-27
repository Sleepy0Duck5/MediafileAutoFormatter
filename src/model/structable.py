import os

from abc import ABCMeta


def extract_title(absolute_path: str) -> str:
    return absolute_path.split(os.sep)[-1]


class Structable(metaclass=ABCMeta):
    def get_title(self) -> str:
        raise NotImplementedError

    def get_absolute_path(self) -> str:
        raise NotImplementedError
