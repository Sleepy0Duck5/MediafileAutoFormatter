import os

from typing import List, Iterable, Optional
from loguru import logger
from pymkv import MKVFile, MKVTrack

from src.model.file import File
from src.model.structable import Structable
from src.constants import Extensions, FileType
from src.env_configs import EnvConfigs
from src.log_exporter import LogExporter


class MkvSubtitleExtractor:
    def __init__(self, env_configs: EnvConfigs, log_exporter: LogExporter) -> None:
        self._env_configs = env_configs
        self._log_exporter = log_exporter

    def extract_subtitle_file_from_mkv(
        self, media_files: List[File], subtitles: List[Structable]
    ) -> List[Structable]:
        """Try to extract subtitle from mkv file when subtitle file not found for a specific media file."""
        extracted_subtitles = []
        mkv_file_cnt = 0

        for media_file in media_files:
            if media_file.get_extension() != Extensions.MKV:
                continue
            logger.info(
                f"Extracting subtitle file from mkv media file {media_file.get_absolute_path()}",
            )

            mkv_file_cnt += 1

            mkv_file = MKVFile(
                media_file.get_absolute_path(),
            )
            tracks = mkv_file.get_track()
            if not isinstance(tracks, Iterable):
                raise Exception("MKV File's tracks are not iterable")

            # First pass: try to find primary language track
            target_track = None
            is_fallback = False

            for track in tracks:
                if self._validate_subtitle_track(track=track, lang=self._env_configs.MKV_SUBTITLE_EXTRACTION_LANGUAGE):
                    target_track = track
                    break
            
            # Second pass: try to find fallback language track if primary not found
            fallback_langs = getattr(self._env_configs, "MKV_SUBTITLE_FALLBACK_LANGUAGE", [])
            if not isinstance(fallback_langs, list):
                fallback_langs = [fallback_langs]

            if not target_track and fallback_langs:
                for fallback_lang in fallback_langs:
                    for track in tracks:
                        if self._validate_subtitle_track(track=track, lang=fallback_lang):
                            target_track = track
                            is_fallback = True
                            break
                    if target_track:
                        break
            
            if not target_track:
                continue

            subtitle_type = self._get_subtitle_type(track_codec=target_track.track_codec)
            if not subtitle_type:
                logger.info(
                    f"""Valid subtitle found, but cannot determine subtitle type (track_codec={target_track.track_codec}).
                    Skiping extraction for ({media_file.get_absolute_path()})""",
                )
                continue

            new_subtitle_file_path = (
                f"{media_file.get_absolute_path()}.extractedsub.{subtitle_type}"
            )

            extracted_subtitle_path = target_track.extract()
            os.rename(extracted_subtitle_path, new_subtitle_file_path)
            
            extracted_file = File(
                absolute_path=new_subtitle_file_path,
                file_type=FileType.SUBTITLE,
            )

            if is_fallback and getattr(self._env_configs, "ENABLE_SUBTITLE_TRANSLATION", False):
                from src.translator.subtitle_translator import SubtitleTranslator
                translator = SubtitleTranslator(env_configs=self._env_configs)
                try:
                    translated_path = translator.translate_subtitle(extracted_file)
                    # Use the translated file for restructuring
                    extracted_file = File(
                        absolute_path=translated_path,
                        file_type=FileType.SUBTITLE,
                    )
                    self._log_exporter.append_log(
                        f"[TRANSLATED] Fallback subtitle translated and saved to {translated_path}.",
                        silent=False,
                    )
                except Exception as e:
                    logger.error(f"Failed to translate subtitle {new_subtitle_file_path}: {e}")
                    self._log_exporter.append_log(
                        f"[TRANSLATION_FAILED] Failed to translate {new_subtitle_file_path}: {e}",
                        silent=False,
                    )

            extracted_subtitles.append(extracted_file)

            self._log_exporter.append_log(
                f"[EXTRACTED] New Subtitle extracted from {media_file.get_absolute_path()}, subtitle {extracted_file.get_absolute_path()} created.",
                silent=False,
            )

        if len(extracted_subtitles) == 0:
            self._log_exporter.append_log(
                f"[EXTRACTED] No subtitle extracted from mkv files(mkv_file_cnt={mkv_file_cnt})",
                silent=False,
            )
            return subtitles + extracted_subtitles

        logger.info(
            f"Total {len(extracted_subtitles)} subtitle files extracted from mkv files",
        )

        return subtitles + extracted_subtitles

    def _validate_subtitle_track(self, track: MKVTrack, lang: str) -> bool:
        if not self._is_subtitle_track(track=track):
            return False

        if track.language != lang:
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
