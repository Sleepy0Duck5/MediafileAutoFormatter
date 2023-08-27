from abc import ABCMeta


class Formatter(metaclass=ABCMeta):
    def format():
        pass


class GeneralFormatter(Formatter):
    def format():
        raise NotImplementedError
