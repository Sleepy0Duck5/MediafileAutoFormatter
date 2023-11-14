class RestructorException(Exception):
    pass


class SeasonNotFoundException(RestructorException):
    pass


class NoMeidaFileException(RestructorException):
    pass


class SubtitleIndexDuplicatedException(RestructorException):
    pass


class NoSubtitleFileException(RestructorException):
    pass
