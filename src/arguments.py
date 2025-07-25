import argparse

from loguru import logger
from dataclasses import dataclass
from typing import Optional


@dataclass
class Arguments:
    source_path: str
    target_path: str
    multiple: bool
    mkv_audio_language: Optional[str]

    def print(self):
        logger.info(f"arguments: {self.__dict__}")


class ArgumentParser:
    def __init__(self):
        self._parser = argparse.ArgumentParser()

        self._parser.add_argument("source_path", type=str)
        self._parser.add_argument("--target_path", type=str, default="", required=True)
        self._parser.add_argument(
            "--multiple", type=bool, default=False, required=False
        )
        self._parser.add_argument(
            "--mkv_audio_language", type=str, default=None, required=False
        )

    def get_arguments(self) -> Arguments:
        raw_args = self._parser.parse_args()

        arguments = Arguments(
            source_path=raw_args.source_path,
            target_path=raw_args.target_path,
            multiple=raw_args.multiple,
            mkv_audio_language=raw_args.mkv_audio_language,
        )

        arguments.print()

        return arguments
