import os
from abc import ABCMeta
from patoolib import extract_archive
from loguru import logger

from src.model.file import File
from src.model.folder import Folder, RestructedFolder
from src.model.metadata import Metadata, MovieMetadata
from src.formatter.formatter import Formatter
from src.env_configs import EnvConfigs
from src.errors import TargetPathNotFoundException, InvalidMediaTypeException
from src.constants import FileType, Constants


class RestructLogger(metaclass=ABCMeta):
    def __init__(self) -> None:
        raise NotImplementedError

    def log(self) -> None:
        raise NotImplementedError


class GeneralRestructLogger(RestructLogger):
    def __init__(self) -> None:
        pass

    def log(self) -> None:
        pass
