import os
from loguru import logger
from typing import List

from src.model.structable import Structable
from src.model.file import File, RestructedFile
from src.model.folder import Folder
from src.restructor.restructor import GeneralRestructor
from src.model.metadata import (
    MovieMetadata,
    SubtitleContainingMetadata,
)
from src.restructor.errors import (
    NoMeidaFileException,
)


class MovieRestructor(GeneralRestructor):
    def restruct(self, metadata: MovieMetadata, target_path: str) -> Folder:
        root_folder = super().restruct(metadata=metadata, target_path=target_path)

        self._restruct_subtitle(
            root_folder=root_folder,
            subtitles=metadata.get_subtitles(),
            metadata=metadata,
        )

        self._restruct_mediafile(root_folder=root_folder, metadata=metadata)

        self._export_restruct_log(root_folder=root_folder)

        return root_folder

    def _restruct_subtitle(
        self,
        root_folder: Folder,
        subtitles: List[Structable],
        metadata: MovieMetadata,
    ) -> None:
        if len(subtitles) <= 0:
            return

        for subtitle_struct in subtitles:
            subtitle_files = self._get_subtitle_files(
                subtitle_struct=subtitle_struct, metadata=metadata
            )

            if len(subtitle_files) >= 0:
                self._rename_subtitle_and_append(
                    root_folder=root_folder,
                    metadata=metadata,
                    subtitle_files=subtitle_files,
                )

                self._subtitle_backup(
                    subtitle_files=[subtitle_struct],
                    root_folder=root_folder,
                )
                return

    def _rename_subtitle_and_append(
        self, root_folder: Folder, metadata: MovieMetadata, subtitle_files: List[File]
    ) -> None:
        try:
            media_files = metadata.get_media_files()
            if len(media_files) <= 0:
                raise NoMeidaFileException

            if len(subtitle_files) <= 0:
                return

            subtitle_file = subtitle_files[0]

            new_file_name = self._formatter.rename_subtitle_file(
                metadata=metadata, subtitle_file=subtitle_file
            )

            new_file_path = os.path.join(root_folder.get_absolute_path(), new_file_name)

            restructed_subtitle_file = RestructedFile(
                absolute_path=new_file_path,
                original_file=subtitle_file,
            )

            self._append_struct_to_folder(
                folder=root_folder, struct=restructed_subtitle_file
            )
        except Exception as e:
            self._log_exporter.append_log(
                f"[WARNING] Failed to rename subtitles : {str(e)}", silent=False
            )

    def _restruct_mediafile(
        self, root_folder: Folder, metadata: SubtitleContainingMetadata
    ) -> None:
        media_file_names = {}

        for original_file in metadata.get_media_files():
            new_title = self._formatter.rename_file(
                metadata=metadata, file=original_file
            )
            new_file_name = f"{new_title}.{original_file.get_extension()}"

            # Add index to file name if same media file name exists
            if not media_file_names.get(new_file_name):
                media_file_names[new_file_name] = 0
            else:
                index = media_file_names.get(new_file_name)
                media_file_names[new_file_name] += 1
                new_file_name = f"{new_title}({index}).{original_file.get_extension()}"

            new_path = os.path.join(root_folder.get_absolute_path(), new_file_name)

            restructed_media_file = RestructedFile(
                absolute_path=new_path, original_file=original_file
            )

            self._audio_track_changer.change_audio_track(file=original_file)

            self._append_struct_to_folder(
                folder=root_folder, struct=restructed_media_file
            )
