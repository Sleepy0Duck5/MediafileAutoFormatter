import shutil

from typing import Optional, Iterable, Tuple
from pymkv import MKVFile, MKVTrack
from loguru import logger

from src.model.file import File
from src.constants import Extensions


class AudioTrackChanger:
    def __init__(self, audio_track_langugage: Optional[str]):
        self._audio_track_langugage = audio_track_langugage

    def change_audio_track(self, file: File) -> None:
        if not self._audio_track_langugage:
            return

        if file.get_extension() != Extensions.MKV:
            return

        logger.info(f"Try to change default audio track for {file.get_absolute_path()}")

        mkv_file = MKVFile(file_path=file.get_absolute_path())

        default_audio_track, new_default_audio_track = self._find_default_tracks(
            mkv_file=mkv_file
        )

        if default_audio_track and (
            default_audio_track.language == self._audio_track_langugage
        ):
            logger.info(
                f"Default audio track's lanuage is already {default_audio_track.language}({default_audio_track.track_name}), Skipping audio track change task..."
            )
            return

        if not new_default_audio_track:
            logger.info(
                "New default audio track not found, aborting change audio track..."
            )
            return

        logger.info(
            f"New default {new_default_audio_track.language} audio track found! ({new_default_audio_track.track_name})"
        )

        try:
            output_file_path = file.get_absolute_path() + "_audio_track_changed.mkv"

            self._change_default_audio_track_flags_and_apply(
                mkv_file=mkv_file,
                default_audio_track=default_audio_track,
                new_default_audio_track=new_default_audio_track,
                output_file_path=output_file_path,
            )

        except Exception as e:
            logger.opt(exception=e).warning(
                f"Failed to change default audio track, aborting file{file.get_absolute_path()}"
            )
            return

        # replace original mkv file
        try:
            shutil.move(src=output_file_path, dst=file.get_absolute_path())
        except Exception as e:
            logger.opt(exception=e).warning(
                f"Failed to replace audio changed mkv, aborting file {file.get_absolute_path()}"
            )

        logger.info(
            f"Default audio track changed into {new_default_audio_track.track_name} (filepath={file.get_absolute_path()})"
        )

    def _find_default_tracks(
        self, mkv_file: MKVFile
    ) -> Tuple[Optional[MKVTrack], Optional[MKVTrack]]:
        tracks = mkv_file.get_track()
        if not isinstance(tracks, Iterable):
            raise Exception("MKV File's tracks are not iterable")

        default_audio_track = None
        new_default_audio_track = None

        for track in tracks:
            if not self._is_audio_track(track=track):
                continue

            if (track.default_track) and default_audio_track is None:
                default_audio_track = track

            if (
                track.language == self._audio_track_langugage
            ) and new_default_audio_track is None:
                new_default_audio_track = track

        return default_audio_track, new_default_audio_track

    def _is_audio_track(self, track: MKVTrack) -> bool:
        if not track.track_type:
            return False
        return track.track_type.lower().__contains__("audio")

    def _change_default_audio_track_flags_and_apply(
        self,
        mkv_file: MKVFile,
        default_audio_track: Optional[MKVTrack],
        new_default_audio_track: MKVTrack,
        output_file_path: str,
    ) -> None:
        if default_audio_track:
            self._change_default_track_flag(
                mkv_file=mkv_file, track=default_audio_track, default_track_flag=False
            )

        self._change_default_track_flag(
            mkv_file=mkv_file, track=new_default_audio_track, default_track_flag=True
        )

        mkv_file.mux(output_path=output_file_path, silent=True)

    def _change_default_track_flag(
        self, mkv_file: MKVFile, track: MKVTrack, default_track_flag: bool
    ) -> None:
        track.default_track = default_track_flag
        mkv_file.replace_track(track_num=track.track_id, track=track)
