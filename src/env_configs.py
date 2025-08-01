import os
import json
from dotenv import load_dotenv

from src.constants import DefaultEnvConifgs
from src.errors import InvalidEnvConfig


class EnvConfigs:
    def __init__(self) -> None:
        load_dotenv(verbose=True)

        self._FILENAME_FORMAT = os.getenv(
            "FILENAME_FORMAT", DefaultEnvConifgs.FILENAME_FORMAT
        )
        self._SEASON_NUMBER_DIGIT = int(
            os.getenv("SEASON_NUMBER_DIGIT", DefaultEnvConifgs.SEASON_NUMBER_DIGIT)
        )
        self._EPISODE_NUMBER_DIGIT = int(
            os.getenv("EPISODE_NUMBER_DIGIT", DefaultEnvConifgs.EPISODE_NUMBER_DIGIT)
        )
        self._MEDIA_EXTENSIONS = json.loads(
            os.getenv("MEDIA_EXTENSIONS", DefaultEnvConifgs.MEDIA_EXTENSIONS),
        )
        self._SUBTITLE_SUFFIX = os.getenv(
            "SUBTITLE_SUFFIX", DefaultEnvConifgs.SUBTITLE_SUFFIX
        )
        self.MKV_SUBTITLE_EXTRACTION_LANGUAGE = os.getenv(
            "MKV_SUBTITLE_EXTRACTION_LANGUAGE",
            DefaultEnvConifgs.MKV_SUBTITLE_EXTRACTION_LANGUAGE,
        )
        self._CONVERT_SMI = (
            os.getenv(
                "CONVERT_SMI",
                DefaultEnvConifgs.CONVERT_SMI,
            )
            == "True"
        )
        self._CONVERT_SMI_EXTENSION = os.getenv(
            "CONVERT_SMI_EXTENSION",
            DefaultEnvConifgs.CONVERT_SMI_EXTENSION,
        )
        self._SUBTITLE_EXTENSIONS = json.loads(
            os.getenv("SUBTITLE_EXTENSIONS", DefaultEnvConifgs.SUBTITLE_EXTENSIONS)
        )
        self._EXPORT_DEBUG_LOG_FILE = (
            os.getenv(
                "EXPORT_DEBUG_LOG_FILE",
                DefaultEnvConifgs.EXPORT_DEBUG_LOG_FILE,
            )
            == "True"
        )

        self._validation()

    def _validation(self):
        self._validate_filename_format(filename_format=self._FILENAME_FORMAT)
        self._validate_number_digit(number_digit=self._SEASON_NUMBER_DIGIT)
        self._validate_number_digit(number_digit=self._EPISODE_NUMBER_DIGIT)

    def _validate_filename_format(self, filename_format: str):
        essential_args = ["title", "season_number", "episode_number"]

        for essential_arg in essential_args:
            if not (essential_arg in filename_format):
                raise InvalidEnvConfig(
                    f"No {essential_arg} in FILENAME_FORMAT, check .env file"
                )

    def _validate_number_digit(self, number_digit: int):
        if number_digit <= 0:
            raise InvalidEnvConfig(
                f"Invalid NUMBER_DIGIT '{number_digit}' in env config, check .env file"
            )
