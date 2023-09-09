class AnalyzerException(Exception):
    pass


class MediaRootNotFoundException(AnalyzerException):
    pass


class MediaNotFoundException(AnalyzerException):
    pass


class TargetPathNotFoundException(Exception):
    pass


class MetadataBuildException(AnalyzerException):
    pass


class InvalidMediaTypeException(Exception):
    pass


class InvalidMetadataTypeException(Exception):
    pass


class FormatterException(Exception):
    pass


class InvalidFolderNameException(FormatterException):
    pass
