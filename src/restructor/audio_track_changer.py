import subprocess

from typing import Optional, Iterable, List
from pymkv import MKVFile, MKVTrack
from loguru import logger

from src.model.file import File
from src.constants import Extensions
from src.log_exporter import LogExporter


class AudioTrackChanger:
    def __init__(self, log_exporter: LogExporter, audio_track_langugage: Optional[str]):
        self._log_exporter = log_exporter
        self._audio_track_langugage = audio_track_langugage

    def change_audio_track(self, file: File) -> None:
        if not self._audio_track_langugage:
            return

        if file.get_extension() != Extensions.MKV:
            return

        logger.info(f"Try to change default audio track for {file.get_absolute_path()}")

        mkv_file = MKVFile(file_path=file.get_absolute_path())

        audio_tracks = self._find_audio_tracks(mkv_file=mkv_file)

        wanted_audio_track = self._find_wanted_language_audio_track(tracks=audio_tracks)

        if not wanted_audio_track:
            return

        try:
            self._change_default_audio_track(
                file_path=file.get_absolute_path(),
                tracks=audio_tracks,
                wanted_audio_track=wanted_audio_track,
            )
        except Exception as e:
            self._log_exporter.append_log(
                f"Failed to change default audio track, aborting file{file.get_absolute_path()}, error={e}",
                silent=False,
            )
            # rollback?
            return

        self._log_exporter.append_log(
            f"[CHANGED] Default audio track changed into {wanted_audio_track.language}, {wanted_audio_track.track_name} (filepath={file.get_absolute_path()})",
            silent=False,
        )

    def _find_audio_tracks(self, mkv_file: MKVFile) -> List[MKVTrack]:
        tracks = mkv_file.get_track()
        if not isinstance(tracks, Iterable):
            raise Exception("MKV File's tracks are not iterable")

        audio_tracks = []

        for track in tracks:
            if not self._is_audio_track(track=track):
                continue

            audio_tracks.append(track)

        return audio_tracks

    def _is_audio_track(self, track: MKVTrack) -> bool:
        if not track.track_type:
            return False
        return track.track_type.lower().__contains__("audio")

    def _find_wanted_language_audio_track(
        self, tracks: List[MKVTrack]
    ) -> Optional[MKVTrack]:
        for track in tracks:
            if track.language != self._audio_track_langugage:
                continue

            if track.default_track:
                logger.info(
                    f"Default audio track's lanuage is already {track.language}({track.track_name}), Skipping audio track change task..."
                )
                return None

            return track

        logger.info(
            f"Wanted language audio track not found, Skipping audio track change task..."
        )
        return None

    def _change_default_audio_track(
        self,
        file_path: str,
        tracks: List[MKVTrack],
        wanted_audio_track: MKVTrack,
    ) -> None:
        command = f'mkvpropedit -v "{file_path}" '

        for idx, track in enumerate(tracks):
            flag_default = "0"
            if track == wanted_audio_track:
                flag_default = "1"

            command += f"--edit track:a{idx + 1} --set flag-default={flag_default} "

        logger.info(f"mkvpropedit command: {command}")

        subprocess.call(command)
