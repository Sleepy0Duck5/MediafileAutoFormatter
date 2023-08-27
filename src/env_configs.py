import os
import json
from dotenv import load_dotenv

from src.constants import DefaultEnvConifgs


class EnvConfigs:
    def __init__(self) -> None:
        load_dotenv(verbose=True)

        self._FILENAME_FORMAT = os.getenv(
            "FILENAME_FORMAT", DefaultEnvConifgs.FILENAME_FORMAT
        )
        self._MEDIA_EXTENSIONS = json.loads(
            os.getenv("MEDIA_EXTENSIONS", DefaultEnvConifgs.MEDIA_EXTENSIONS),
        )
        self._SUBTITLE_SUFFIX = os.getenv(
            "SUBTITLE_SUFFIX", DefaultEnvConifgs.SUBTITLE_SUFFIX
        )
        self._CONVERT_SUBTITLE_EXTENSION = bool(
            os.getenv(
                "CONVERT_SUBTITLE_EXTENSION",
                DefaultEnvConifgs.CONVERT_SUBTITLE_EXTENSION,
            )
        )
        self._SUBTITLE_EXTENSIONS = json.loads(
            os.getenv("SUBTITLE_EXTENSIONS", DefaultEnvConifgs.SUBTITLE_EXTENSIONS)
        )
        self._FALLBACK_SUBTITLE_EXTENSION = os.getenv(
            "FALLBACK_SUBTITLE_EXTENSION", DefaultEnvConifgs.FALLBACK_SUBTITLE_EXTENSION
        )
        self._FILE_WATCH = bool(os.getenv("FILE_WATCH", DefaultEnvConifgs.FILE_WATCH))
        self._FILE_WATCH_SOURCE_PATH = os.getenv(
            "FILE_WATCH_SOURCE_PATH", DefaultEnvConifgs.FILE_WATCH_SOURCE_PATH
        )
        self._FILE_WATCH_TARGET_PATH = os.getenv(
            "FILE_WATCH_TARGET_PATH", DefaultEnvConifgs.FILE_WATCH_TARGET_PATH
        )
