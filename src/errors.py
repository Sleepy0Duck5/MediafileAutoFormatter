class GeneralException(Exception):
    pass


class DirectoryNotFoundException(GeneralException):
    pass


class InvalidMediaTypeException(GeneralException):
    pass


class InvalidMetadataTypeException(GeneralException):
    pass
