import os
from loguru import logger
from typing import List, Dict

from src.model.structable import Structable
from src.model.file import File, RestructedFile
from src.model.folder import Folder
from src.model.metadata import (
    TVMetadata,
    SeasonMetadata,
)
from src.formatter.formatter import TVFormatter
from src.formatter.subtitle_converter import SubtitleConverter
from src.restructor.subtitle_extractor import (
    SubtitleExtractor,
)
from src.restructor.restructor import GeneralRestructor
from src.restructor.subtitle_syncer import SubtitleSyncer
from src.restructor.errors import (
    SeasonNotFoundException,
    NoMeidaFileException,
)
from src.analyzer.media_analyzer import TVAnalyzer
from src.env_configs import EnvConfigs
from src.constants import SeasonAlias


class TVRestructor(GeneralRestructor):
    def __init__(
        self,
        env_configs: EnvConfigs,
        formatter: TVFormatter,
        subtitle_extractor: SubtitleExtractor,
        subtitle_analyzer: TVAnalyzer,
        subtitle_converter: SubtitleConverter,
        subtitle_syncer: SubtitleSyncer,
    ) -> None:
        super().__init__(
            env_configs,
            formatter,
            subtitle_extractor,
            subtitle_converter,
            subtitle_syncer,
        )
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
                subtitle_files = subtitles_by_episode[episode_index]

                index = 0
                for subtitle_file in subtitle_files:
                    new_title = self._formatter.rename_file(
                        metadata=metadata,
                        file=subtitle_file,
                        episode_index=episode_index,
                    )

                    if len(subtitle_files) <= 1:
                        new_suffix = self._env_configs._SUBTITLE_SUFFIX
                    else:
                        new_suffix = self._formatter.extract_subtitle_original_suffix(
                            filename=subtitle_file.get_title()
                        )

                    if index <= 0:
                        new_file_name = (
                            f"{new_title}.{new_suffix}.{subtitle_file.get_extension()}"
                        )
                    else:
                        new_file_name = f"{new_title}.{new_suffix} ({index}).{subtitle_file.get_extension()}"

                    index += 1

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
            logger.warning(f"Failed to rename subtitles : {e}")
            self._log += f"[WARNING] Failed to rename subtitles : {e}"

    def _organaize_subtitles_by_episode(self, subtitle_files: List[File]) -> Dict:
        subtitles_by_episode = {}

        subtitle_files_prefix = self._subtitle_analyzer._get_file_name_prefix(
            files=subtitle_files
        )

        for subtitle_file in subtitle_files:
            episode_index = (
                self._subtitle_analyzer._extract_episode_index_from_file_name(
                    file_name=subtitle_file.get_title(), prefix=subtitle_files_prefix
                )
            )

            if subtitles_by_episode.get(episode_index):
                subtitles_by_episode[episode_index].append(subtitle_file)
            else:
                subtitles_by_episode[episode_index] = [subtitle_file]

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
