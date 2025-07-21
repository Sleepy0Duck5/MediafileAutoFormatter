from typing import List

from src.model.file import File
from src.constants import FileType
from src.formatter.subtitle_converter import SubtitleConverter
from src.formatter.library.smi2ass import convert_smi_file_to_ass_file


class SmiToAssConverter(SubtitleConverter):
    def convert_subtitle(self, file: File) -> List[File]:
        ass_file_paths = convert_smi_file_to_ass_file(smi_path=file.get_absolute_path())

        converted_files = []

        for ass_file_path in ass_file_paths:
            converted_files.append(
                File(absolute_path=ass_file_path, file_type=FileType.SUBTITLE)
            )

        if len(converted_files) <= 0:
            raise Exception(
                "Failed to convert smi subtitle into ass : no converted_files"
            )

        return converted_files
