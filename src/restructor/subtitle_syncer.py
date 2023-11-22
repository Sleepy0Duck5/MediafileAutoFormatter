import tempfile

from abc import ABCMeta
from typing import Optional
from ffsubsync import ffsubsync
from loguru import logger

from src.constants import FileType
from src.model.file import File


class SubtitleSyncer(metaclass=ABCMeta):
    def __init__(self) -> None:
        raise NotImplementedError

    def sync_subtitle(self, subtitle: File, media_file: File) -> File:
        raise NotImplementedError


class GeneralSubtitleSyncer(SubtitleSyncer):
    def sync_subtitle(self, subtitle: File, media_file: File) -> Optional[File]:
        try:
            temp_file = tempfile.NamedTemporaryFile(delete=False)

            unparsed_args = [
                media_file.get_absolute_path(),
                "-i",
                subtitle.get_absolute_path,
                "-o",
                temp_file.name,
            ]

            parser = ffsubsync.make_parser()
            args = parser.parse_args(unparsed_args)

            ffsubsync.run(args)

            return File(absolute_path=temp_file.name, file_type=FileType.SUBTITLE)
        except Exception as e:
            logger.warning(e)

        return None
