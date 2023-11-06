from enum import Enum


class Constants:
    METADATA_FILENAME = "metadata"
    UNKNOWN = "unknown"
    MAXIMUM_ARCHIVE_SIZE = 30000000  # 30MB
    MAXIMUM_FOLDER_NAME_LENGTH = 250
    ERROR_LOG_FILENAME = "MAF_Error"
    SUBTITLE_BACKUP_DIRECTORY_NAME = "MAF_SubtitleBackup"


class Log:
    LOG_FILE_NAME = "mediafile_auto_formatter.log"
    LOG_FILE_ROTATION = "50 MB"


class Extensions:
    TXT = "txt"
    NFO = "nfo"
    LOG = "log"


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
    FILENAME_FORMAT = "{{ title }} - S{{ season_number }}E{{ episode_number }}"
    SEASON_NUMBER_DIGIT = 2
    EPISODE_NUMBER_DIGIT = 2
    MEDIA_EXTENSIONS = '["avi", "mp4", "mkv"]'
    SUBTITLE_SUFFIX = "ko"
    CONVERT_SUBTITLE_EXTENSION = False
    SUBTITLE_EXTENSIONS = '["smi", "ass"]'
    FALLBACK_SUBTITLE_EXTENSION = "srt"


class SeasonAlias:
    KOR_1 = "시즌"
    ENG_1 = "season"
