import os

from abc import ABCMeta


class Structable(metaclass=ABCMeta):
    def _extract_title(self, absolute_path: str) -> str:
        raise NotImplementedError

    def get_title(self) -> str:
        raise NotImplementedError

    def get_absolute_path(self) -> str:
        raise NotImplementedError

    def explain(self) -> str:
        return ""
