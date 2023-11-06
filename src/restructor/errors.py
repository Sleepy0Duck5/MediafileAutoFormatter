class RestructorException(Exception):
    pass


class SeasonNotFoundException(RestructorException):
    pass


class NoMeidaFileException(RestructorException):
    pass


class SubtitleIndexDuplicatedException(RestructorException):
    pass
