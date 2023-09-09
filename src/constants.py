from enum import Enum


class Constants:
    METADATA_FILENAME = "metadata"
    UNKNOWN = "unknown"
    MAXIMUM_ARCHIVE_SIZE = 30000000  # 30MB
    MAXIMUM_FOLDER_NAME_LENGTH = 250
    TEMP_SUBTITLE_FOLDER_NAME = "tmp_mediafile_auto_formatter_extracted_subtitle"
    FILENAME_INDEX_ZFILL = 3


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
    EXTRA = 5
    UNKNOWN = 9


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

class SeasonAlias:
    KOR_1 = "시즌"
    ENG_1 = "season"