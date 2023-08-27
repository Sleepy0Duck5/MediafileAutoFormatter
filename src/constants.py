from enum import Enum


class Constants:
    METADATA_FILENAME = "metadata"
    UNKNOWN = "unknown"


class Extensions:
    TXT = "txt"
    NFO = "nfo"


class MediaType(Enum):
    MOVIE = 1
    TV = 2


class FileType(Enum):
    MEDIA = 1
    SUBTITLE = 2
    ARCHIVED_SUBTITLE = 3
    NFO = 4
    EXTRA = 9


class DefaultEnvConifgs:
    FILENAME_FORMAT = (
        "{{ title }} - S{{ season_number }}E{{ episode_number }} - {{ extras }}"
    )
    MEDIA_EXTENSIONS = '["avi", "mp4", "mkv"]'
    SUBTITLE_SUFFIX = "ko"
    CONVERT_SUBTITLE_EXTENSION = False
    SUBTITLE_EXTENSIONS = '["smi", "ass"]'
    FALLBACK_SUBTITLE_EXTENSION = "srt"
    FILE_WATCH = False
    FILE_WATCH_SOURCE_PATH = "/"
    FILE_WATCH_TARGET_PATH = "/"
