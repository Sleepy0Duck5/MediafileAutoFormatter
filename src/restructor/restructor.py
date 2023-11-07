import os
import tempfile
import shutil
from abc import ABCMeta
from loguru import logger
from typing import List

from src.model.structable import Structable
from src.model.file import File, RestructedFile
from src.model.folder import Folder, RestructedFolder
from src.model.metadata import (
    Metadata,
    MovieMetadata,
    TVMetadata,
    SubtitleContainingMetadata,
    SeasonMetadata,
)
from src.formatter.formatter import Formatter, TVFormatter
from src.formatter.subtitle_converter import SubtitleConverter
from src.restructor.subtitle_extractor import (
    SubtitleExtractor,
)
from src.restructor.errors import (
    SeasonNotFoundException,
    NoMeidaFileException,
    SubtitleIndexDuplicatedException,
)
from src.analyzer.media_analyzer import TVAnalyzer
from src.env_configs import EnvConfigs
from src.errors import DirectoryNotFoundException
from src.constants import FileType, Constants, Extensions, SeasonAlias


class Restructor(metaclass=ABCMeta):
    def __init__(self, env_configs: EnvConfigs, formatter: Formatter) -> None:
        raise NotImplementedError

    def restruct(self, metadata: Metadata, target_path: str) -> RestructedFolder:
        raise NotImplementedError

    def _extract_subtitle(self, metadata: Metadata) -> dict[int, Folder]:
        raise NotImplementedError


class GeneralRestructor(Restructor):
    def __init__(
        self,
        env_configs: EnvConfigs,
        formatter: Formatter,
        subtitle_extractor: SubtitleExtractor,
        subtitle_converter: SubtitleConverter,
    ) -> None:
        self._env_configs = env_configs
        self._formatter = formatter
        self._subtitle_extractor = subtitle_extractor
        self._subtitle_converter = subtitle_converter
        self._log = ""

    def restruct(self, metadata: Metadata, target_path: str) -> Folder:
        if not os.path.exists(path=target_path):
            raise DirectoryNotFoundException

        self._log += metadata.explain() + "\n"

        root_folder = self._create_new_root_folder(
            metadata=metadata, target_path=target_path
        )

        return root_folder

    def _create_new_root_folder(self, metadata: Metadata, target_path: str) -> Folder:
        root_folder_title = self._formatter.format_name(name=metadata.get_title())

        new_root_absoluth_path = os.path.join(target_path, root_folder_title)

        new_root_folder = Folder(absolute_path=new_root_absoluth_path)

        self._append_restruct_log(new_root_folder)

        return new_root_folder

    def _export_restruct_log(self, root_folder: Folder) -> None:
        temp_file = tempfile.NamedTemporaryFile(delete=False)
        temp_file.write(self._log.encode("utf-8"))
        temp_file.flush()

        log_path = os.path.join(root_folder.get_absolute_path(), "MAF_Restruct.log")
        log_file = RestructedFile(
            absolute_path=log_path,
            original_file=File(absolute_path=temp_file.name, file_type=FileType.EXTRA),
        )

        try:
            os.chmod(temp_file.name, Constants.DEFAULT_PERMISSION_FOR_LOG_FILE)
        except Exception as e:
            logger.warning(
                f"Failed to grant permission {Constants.DEFAULT_PERMISSION_FOR_LOG_FILE} to {temp_file.name}, error : {str(e)}"
            )

        root_folder.append_struct(log_file)
        self._log = ""

    def _restruct_subtitle(
        self,
        root_folder: Folder,
        subtitles: List[Structable],
        metadata: Metadata,
    ) -> None:
        raise NotImplementedError

    def _get_subtitle_files(
        self,
        subtitle_struct: Structable,
        metadata: Metadata,
    ) -> List[File]:
        subtitle_files = []

        if isinstance(subtitle_struct, File):
            if subtitle_struct.get_file_type() == FileType.SUBTITLE:
                subtitle_files = [subtitle_struct]
            elif subtitle_struct.get_file_type() == FileType.ARCHIVED_SUBTITLE:
                extracted_folder = self._subtitle_extractor.extract_archived_subtitle(
                    subtitle=subtitle_struct, metadata=metadata
                )
                subtitle_files = self._get_subtitles_from_folder(
                    folder=extracted_folder
                )
        elif isinstance(subtitle_struct, Folder):
            subtitle_files = self._get_subtitles_from_folder(folder=subtitle_struct)

        if len(subtitle_files) <= 0:
            logger.warning("Subtitle found but nothing selected")
            self._log += "[WARNING] Subtitle found but nothing selected"

        return self._convert_subtitle(subtitle_files=subtitle_files)

    def _convert_subtitle(self, subtitle_files: List[File]) -> List[File]:
        if not self._env_configs._CONVERT_SMI_TO_SRT:
            return subtitle_files

        result = []

        for subtitle_file in subtitle_files:
            if subtitle_file.get_extension() == Extensions.SMI:
                try:
                    converted_files = self._subtitle_converter.convert_smi_to_srt(
                        file=subtitle_file
                    )
                    result.extend(converted_files)
                    logger.info(
                        f"smi subtitle converted into srt : {subtitle_file.get_absolute_path()}"
                    )
                    self._log += f"[CONVERTED] smi subtitle converted into srt : {subtitle_file.get_absolute_path()}"
                except Exception:
                    logger.warning(
                        f"Failed to convert subtitle : {subtitle_file.get_absolute_path()}"
                    )
                    self._log += f"[WARNING] Failed to convert subtitle : {subtitle_file.get_absolute_path()}"
                    result.append(subtitle_file)
            else:
                result.append(subtitle_file)

        return result

    def _get_subtitles_from_folder(self, folder: Folder) -> List[File]:
        subtitles = []

        for subtitle in folder.get_files():
            if subtitle.get_file_type() == FileType.SUBTITLE:
                subtitles.append(subtitle)

        return subtitles

    def _subtitle_backup(
        self, subtitle_files: List[Structable], root_folder: Folder
    ) -> None:
        # Create backup folder
        backup_path = os.path.join(
            root_folder.get_absolute_path(), Constants.SUBTITLE_BACKUP_DIRECTORY_NAME
        )
        backup_folder = Folder(absolute_path=backup_path)

        for file in subtitle_files:
            if isinstance(file, File):
                # Copy subtitle file
                backup_file_name = file.get_absolute_path().split(sep=os.sep)[-1]

                temp_copied_subtitle_path = os.path.join(
                    tempfile.mkdtemp(),
                    backup_file_name,
                )
                shutil.copy2(file.get_absolute_path(), temp_copied_subtitle_path)

                backup_file = RestructedFile(
                    absolute_path=os.path.join(backup_path, backup_file_name),
                    original_file=File(
                        absolute_path=temp_copied_subtitle_path,
                        file_type=file.get_file_type(),
                    ),
                )

                self._append_struct_to_folder(folder=backup_folder, struct=backup_file)
            else:
                logger.warning("Subtitle folder backup not implemented")
                raise NotImplemented

        self._append_struct_to_folder(folder=root_folder, struct=backup_folder)

    def _restruct_mediafile(
        self, root_folder: Folder, metadata: SubtitleContainingMetadata
    ) -> None:
        raise NotImplementedError

    def _append_restruct_log(self, struct: Structable):
        self._log += struct.explain() + "\n"

    def _append_struct_to_folder(self, folder: Folder, struct: Structable) -> None:
        folder.append_struct(struct=struct)
        self._append_restruct_log(struct=struct)

    def _rename_subtitle_and_append(
        self, root_folder: Folder, metadata: Metadata, subtitle_files: List[File]
    ) -> None:
        raise NotImplementedError


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
            logger.warning(f"Failed to rename subtitles : {str(e)}")
            self._log += f"[WARNING] Failed to rename subtitles : {str(e)}"

    def _restruct_mediafile(
        self, root_folder: Folder, metadata: SubtitleContainingMetadata
    ) -> None:
        media_file_names = {}

        for file in metadata.get_media_files():
            new_title = self._formatter.rename_file(metadata=metadata, file=file)
            new_file_name = f"{new_title}.{file.get_extension()}"

            # Add index to file name if same media file name exists
            if not media_file_names.get(new_file_name):
                media_file_names[new_file_name] = 0
            else:
                index = media_file_names.get(new_file_name)
                media_file_names[new_file_name] += 1
                new_file_name = f"{new_title}({index}).{file.get_extension()}"

            new_path = os.path.join(root_folder.get_absolute_path(), new_file_name)

            restructed_media_file = RestructedFile(
                absolute_path=new_path, original_file=file
            )

            self._append_struct_to_folder(
                folder=root_folder, struct=restructed_media_file
            )


class TVRestructor(GeneralRestructor):
    def __init__(
        self,
        env_configs: EnvConfigs,
        formatter: TVFormatter,
        subtitle_extractor: SubtitleExtractor,
        subtitle_analyzer: TVAnalyzer,
        subtitle_converter: SubtitleConverter,
    ) -> None:
        super().__init__(env_configs, formatter, subtitle_extractor, subtitle_converter)
        self._subtitle_analyzer = subtitle_analyzer

    def restruct(self, metadata: TVMetadata, target_path: str) -> Folder:
        root_folder = super().restruct(metadata=metadata, target_path=target_path)

        seasons = metadata.get_seasons()
        if not seasons:
            raise SeasonNotFoundException

        for index in seasons:
            season_metadata = seasons[index]
            self._log += "\n" + season_metadata.explain() + "\n"

            season_folder = self._create_season_folder(
                root_folder=root_folder, season_metadata=season_metadata
            )

            self._restruct_subtitle(
                root_folder=season_folder,
                subtitles=season_metadata.get_subtitles(),
                metadata=season_metadata,
            )

            self._restruct_mediafile(
                root_folder=season_folder, metadata=season_metadata
            )

        self._export_restruct_log(root_folder=root_folder)

        return root_folder

    def _create_season_folder(
        self, root_folder: Folder, season_metadata: SeasonMetadata
    ) -> Folder:
        season_folder_path = (
            root_folder.get_absolute_path()
            + os.sep
            + f"{SeasonAlias.KOR_1} "
            + str(season_metadata.get_season_index())
        )
        season_folder = Folder(absolute_path=season_folder_path)

        self._append_struct_to_folder(folder=root_folder, struct=season_folder)

        return season_folder

    def _restruct_subtitle(
        self,
        root_folder: Folder,
        subtitles: List[Structable],
        metadata: SeasonMetadata,
    ) -> None:
        if len(subtitles) <= 0:
            return

        original_subtitle_files = []

        if len(subtitles) == 1:
            subtitle_files = self._get_subtitle_files(
                subtitle_struct=subtitles[0], metadata=metadata
            )
            original_subtitle_files.append(subtitles[0])
        else:
            if len(subtitles) != len(metadata.get_episode_files().keys()):
                logger.warning("Subtitle file count is not same as episode files")
                self._log += (
                    "[WARNING] Subtitle file count is not same as episode files"
                )

            subtitle_files = []

            for subtitle in subtitles:
                extracted_subtitle_files = self._get_subtitle_files(
                    subtitle_struct=subtitle, metadata=metadata
                )
                original_subtitle_files.append(subtitle)
                subtitle_files.extend(extracted_subtitle_files)

                if len(extracted_subtitle_files) >= 2:
                    logger.warning(
                        "[WARNING] Multiple subtitle extracted, subtitle file name can be duplicated"
                    )
                    self._log += "[WARNING] Multiple subtitle extracted, subtitle file name can be duplicated"

        if subtitle_files:
            self._rename_subtitle_and_append(
                root_folder=root_folder,
                metadata=metadata,
                subtitle_files=subtitle_files,
            )

            self._subtitle_backup(
                subtitle_files=[file for file in original_subtitle_files],
                root_folder=root_folder,
            )

    def _rename_subtitle_and_append(
        self, root_folder: Folder, metadata: SeasonMetadata, subtitle_files: List[File]
    ) -> None:
        try:
            episodes = metadata.get_episode_files()
            if len(episodes) <= 0:
                raise NoMeidaFileException

            subtitles_by_episode = self._organaize_subtitles_by_episode(
                subtitle_files=subtitle_files
            )

            for episode_index in subtitles_by_episode.keys():
                subtitle_file = subtitles_by_episode[episode_index]

                new_title = self._formatter.rename_file(
                    metadata=metadata,
                    file=subtitle_file,
                    episode_index=episode_index,
                )
                new_file_name = f"{new_title}.{subtitle_file.get_extension()}"

                new_file_path = os.path.join(
                    root_folder.get_absolute_path(), new_file_name
                )

                restructed_subtitle_file = RestructedFile(
                    absolute_path=new_file_path,
                    original_file=subtitle_file,
                )

                self._append_struct_to_folder(
                    folder=root_folder, struct=restructed_subtitle_file
                )
        except Exception as e:
            logger.warning(f"Failed to rename subtitles : {str(e)}")
            self._log += f"[WARNING] Failed to rename subtitles : {str(e)}"

    def _organaize_subtitles_by_episode(self, subtitle_files: List[File]):
        subtitles_by_episode = {}

        subtitle_files_prefix = self._subtitle_analyzer._get_file_name_prefix(
            files=subtitle_files
        )

        for subtitle_file in subtitle_files:
            episode_index = self._subtitle_analyzer._extract_episode_index_by_file_name(
                file_name=subtitle_file.get_title(), prefix=subtitle_files_prefix
            )

            if subtitles_by_episode.get(episode_index):
                raise SubtitleIndexDuplicatedException

            subtitles_by_episode[episode_index] = subtitle_file

        return subtitles_by_episode

    def _restruct_mediafile(
        self, root_folder: Folder, metadata: SeasonMetadata
    ) -> None:
        media_file_names = {}

        episode_files = metadata.get_episode_files()
        for episode_index in episode_files.keys():
            file = episode_files[episode_index]

            new_title = self._formatter.rename_file(
                metadata=metadata, file=file, episode_index=episode_index
            )
            new_file_name = f"{new_title}.{file.get_extension()}"

            # Add index to file name if same media file name exists
            if not media_file_names.get(new_file_name):
                media_file_names[new_file_name] = 0
            else:
                index = media_file_names.get(new_file_name)
                media_file_names[new_file_name] += 1
                new_file_name = f"{new_title} ({index}).{file.get_extension()}"

            new_path = os.path.join(root_folder.get_absolute_path(), new_file_name)

            restructed_media_file = RestructedFile(
                absolute_path=new_path, original_file=file
            )

            self._append_struct_to_folder(
                folder=root_folder, struct=restructed_media_file
            )
