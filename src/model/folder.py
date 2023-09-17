import os
from typing import List, Self, Optional

from src.model.structable import Structable
from src.model.file import File, FileType


class Folder(Structable):
    def __init__(self, absolute_path: str) -> None:
        self._title = self._extract_title(absolute_path=absolute_path)
        self._absolute_path = absolute_path
        self._structs = []
        self._number_of_files_by_type = {}

    def _extract_title(self, absolute_path: str) -> str:
        return absolute_path.rsplit(sep=os.sep, maxsplit=1)[1]

    def get_title(self) -> str:
        return self._title

    def get_absolute_path(self) -> str:
        return self._absolute_path

    def append_struct(self, struct: Structable):
        if isinstance(struct, File):
            self._number_of_files_by_type[struct.get_file_type()] = (
                self._number_of_files_by_type.get(struct.get_file_type(), 0) + 1
            )
        self._structs.append(struct)

    def get_structs(self) -> List[Structable]:
        return self._structs

    def get_files(self) -> List[File]:
        return [x for x in self._structs if isinstance(x, File)]

    def get_folders(self) -> List[Self]:
        return [x for x in self._structs if isinstance(x, Folder)]

    def get_number_of_files_by_type(self, file_type: FileType) -> int:
        return self._number_of_files_by_type.get(file_type, 0)

    def contains_subtitle_file(self) -> bool:
        return (self.get_number_of_files_by_type(file_type=FileType.SUBTITLE) > 0) or (
            self.get_number_of_files_by_type(file_type=FileType.ARCHIVED_SUBTITLE) > 0
        )


class RestructedFolder(Folder):
    def __init__(
        self, absolute_path: str, original_folder: Optional[Folder] = None
    ) -> None:
        super().__init__(absolute_path)
        self._original_folder = original_folder

    def rename(self, new_name: str) -> None:
        self._title = new_name

    def get_original_folder(self) -> Optional[Folder]:
        return self._original_folder
