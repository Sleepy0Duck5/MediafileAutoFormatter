import os
from abc import ABCMeta
from patoolib import extract_archive

from src.model.file import File
from src.model.folder import Folder, RestructedFolder
from src.model.metadata import Metadata, MovieMetadata
from src.formatter.formatter import Formatter
from src.env_configs import EnvConfigs
from src.errors import TargetPathNotFoundException
from src.constants import FileType


class Restructor(metaclass=ABCMeta):
    def __init__(self, env_configs: EnvConfigs, formatter: Formatter) -> None:
        raise NotImplementedError

    def restruct(self, metadata: Metadata, target_path: str) -> Folder:
        raise NotImplementedError


class GeneralRestructor(Restructor):
    def __init__(self, env_configs: EnvConfigs, formatter: Formatter) -> None:
        self._env_configs = env_configs
        self._formatter = formatter

    def restruct(self, metadata: Metadata, target_path: str) -> Folder:
        raise NotImplementedError

    def _create_new_root_folder(
        self, metadata: Metadata, target_path: str
    ) -> RestructedFolder:
        root_folder_title = self._formatter.format_folder_name(
            folder_name=metadata.get_title()
        )

        new_root_absoluth_path = os.path.join(target_path, root_folder_title)

        return RestructedFolder(absolute_path=new_root_absoluth_path)


class MovieRestructor(GeneralRestructor):
    def restruct(self, metadata: MovieMetadata, target_path: str) -> Folder:
        if not os.path.exists(path=target_path):
            raise TargetPathNotFoundException

        restructed_structs = {}

        new_root_folder = self._create_new_root_folder(
            metadata=metadata, target_path=target_path
        )

        for file in metadata.get_media_root().get_files():
            if file.get_file_type() == FileType.MEDIA:
                new_root_folder.append_struct(file)
                restructed_structs[file.get_absolute_path()] = True

        for elem in metadata.get_subtitles():
            # 임시 경로에 압축 해제?
            temp_extracted_subtitle_path = os.path.join(
                metadata.get_root().get_absolute_path(),
                self._formatter.format_folder_name(folder_name=elem.get_title()),
            )

            if isinstance(elem, File) and (
                elem.get_file_type() == FileType.ARCHIVED_SUBTITLE
            ):
                extract_archive(
                    archive=elem.get_absolute_path(),
                    verbosity=-1,
                    outdir=temp_extracted_subtitle_path,
                )

        raise NotImplementedError


class TVRestructor(GeneralRestructor):
    pass
