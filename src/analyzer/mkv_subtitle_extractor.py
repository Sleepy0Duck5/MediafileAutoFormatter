import os

from typing import List, Iterable, Optional
from loguru import logger
from pymkv import MKVFile, MKVTrack

from src.model.file import File
from src.model.structable import Structable
from src.constants import Extensions, FileType
from src.env_configs import EnvConfigs


class MkvSubtitleExtractor:
    def __init__(
        self,
        env_configs: EnvConfigs,
    ) -> None:
        self._env_configs = env_configs

    def extract_subtitle_file_from_mkv(
        self, media_files: List[File], subtitles: List[Structable]
    ) -> List[Structable]:
        """Try to extract subtitle from mkv file when subtitle file not found in directory."""
        if len(subtitles) > 0:
            return []

        extracted_subtitles = []
        mkv_file_cnt = 0

        for media_file in media_files:
            if media_file.get_extension() != Extensions.MKV:
                continue
            logger.info(
                f"Extracting subtitle file from mkv media file {media_file.get_absolute_path()}"
            )
            mkv_file_cnt += 1

            mkvfile = MKVFile(
                media_file.get_absolute_path(),
            )
            tracks = mkvfile.get_track()
            if not isinstance(tracks, Iterable):
                raise Exception()

            for track in tracks:
                if not self._validate_subtitle_track(track=track):
                    continue

                subtitle_type = self._get_subtitle_type(track_codec=track.track_codec)
                if not subtitle_type:
                    logger.info(
                        f"""Valid subtitle found, but cannot determine subtitle type (track_codec={track.track_codec}).
                        Skiping extraction for ({media_file.get_absolute_path()})"""
                    )
                    continue

                new_subtitle_file_path = (
                    f"{media_file.get_absolute_path()}.extractedsub.{subtitle_type}"
                )

                extracted_subtitle_path = track.extract()

                os.rename(extracted_subtitle_path, new_subtitle_file_path)
                extracted_subtitles.append(
                    File(
                        absolute_path=new_subtitle_file_path,
                        file_type=FileType.SUBTITLE,
                    )
                )
                logger.info(f"Subtitle {new_subtitle_file_path} extracted and created.")
                break

        if len(extracted_subtitles) == 0:
            logger.info(
                f"No subtitle extracted from mkv files(mkv_file_cnt={mkv_file_cnt})"
            )
            return []

        logger.info(
            f"Total {len(extracted_subtitles)} subtitle files extracted from mkv files"
        )

        return extracted_subtitles

    def _validate_subtitle_track(self, track: MKVTrack) -> bool:
        if not self._is_subtitle_track(track=track):
            return False

        if track.language != self._env_configs.MKV_SUBTITLE_EXTRACTION_LANGUAGE:
            return False

        return True

    def _is_subtitle_track(self, track: MKVTrack) -> bool:
        if not track.track_type:
            return False
        return track.track_type.lower().__contains__("subtitle")

    def _get_subtitle_type(self, track_codec: Optional[str]) -> Optional[str]:
        if not track_codec:
            return None

        track_codec_lower = track_codec.lower()

        subtitle_type = None

        if track_codec_lower == "substationalpha":
            subtitle_type = Extensions.ASS
        if track_codec_lower == "subrip/srt" or track_codec_lower.__contains__("srt"):
            subtitle_type = Extensions.SRT

        if subtitle_type in self._env_configs._SUBTITLE_EXTENSIONS:
            return subtitle_type

        logger.warning(f"Unsupported subtitle format (track_codec={track_codec}")
        return None
