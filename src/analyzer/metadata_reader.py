from abc import ABCMeta


class MetadataReader(metaclass=ABCMeta):
    def read(self):
        raise NotImplementedError


class GenearlMetadataReader(MetadataReader):
    pass
