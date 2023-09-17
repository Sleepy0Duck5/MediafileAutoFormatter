class AnalyzerException(Exception):
    pass


class MediaRootNotFoundException(AnalyzerException):
    pass


class MediaNotFoundException(AnalyzerException):
    pass


class MetadataBuildException(AnalyzerException):
    pass


class EpisodeIndexNotFoundException(AnalyzerException):
    pass


class FileNamePatternNotFoundException(AnalyzerException):
    pass
