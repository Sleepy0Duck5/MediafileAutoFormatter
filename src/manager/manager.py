from abc import ABCMeta


class Manager(metaclass=ABCMeta):
    def process(self, source_path: str, target_path: str):
        pass


class GeneralManager(Manager):
    pass
