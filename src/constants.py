from enum import Enum


class Constants:
    METADATA_FILENAME = "metadata"
    UNKNOWN = "unknown"
    MAXIMUM_ARCHIVE_SIZE = 30000000  # 30MB
    MAXIMUM_FOLDER_NAME_LENGTH = 250
    ERROR_LOG_FILENAME = "MAF_Error"
    SUBTITLE_BACKUP_DIRECTORY_NAME = "MAF_SubtitleBackup"
    DEFAULT_PERMISSION_FOR_LOG_FILE = 0o755


class Log:
    LOG_FILE_NAME = "mediafile_auto_formatter.log"
    LOG_FILE_ROTATION = "50 MB"


class Extensions:
    TXT = "txt"
    NFO = "nfo"
    LOG = "log"
    SMI = "smi"


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
    CONVERT_SMI_TO_SRT = "True"
    SUBTITLE_EXTENSIONS = '["smi", "ass"]'
    EXPORT_DEBUG_LOG_FILE = "False"


class SeasonAlias:
    KOR_1 = "시즌"
    ENG_1 = "season"
    ENG_2 = "s"

    SEASON_ALIASES = [KOR_1, ENG_1, ENG_2]
