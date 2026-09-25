import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from types import SimpleNamespace
from unittest.mock import Mock, patch

from src.analyzer.mkv_subtitle_extractor import MkvSubtitleExtractor
from src.constants import FileType
from src.log_exporter import LogExporter
from src.model.file import File


def make_track(codec: str, language: str, track_type: str = "subtitles"):
    return SimpleNamespace(
        track_codec=codec,
        language=language,
        track_type=track_type,
    )


class MkvSubtitleExtractorTest(unittest.TestCase):
    def setUp(self):
        env_configs = SimpleNamespace(_SUBTITLE_EXTENSIONS=["ass", "srt"])
        self.extractor = MkvSubtitleExtractor(
            env_configs=env_configs,
            log_exporter=None,
        )

    def test_prefers_ass_when_all_subtitle_languages_are_undefined(self):
        srt_track = make_track("SubRip/SRT", "und")
        ass_track = make_track("SubStationAlpha", "und")

        selected = self.extractor._select_undefined_subtitle_track(
            [srt_track, ass_track]
        )

        self.assertIs(selected, ass_track)

    def test_uses_srt_when_ass_is_not_available(self):
        srt_track = make_track("SubRip/SRT", "und")

        selected = self.extractor._select_undefined_subtitle_track([srt_track])

        self.assertIs(selected, srt_track)

    def test_does_not_use_undefined_track_when_any_subtitle_has_a_language(self):
        und_track = make_track("SubStationAlpha", "und")
        other_track = make_track("SubRip/SRT", "fra")

        selected = self.extractor._select_undefined_subtitle_track(
            [und_track, other_track]
        )

        self.assertIsNone(selected)

    def test_ignores_non_subtitle_tracks_when_checking_languages(self):
        ass_track = make_track("SubStationAlpha", "und")
        audio_track = make_track("AAC", "jpn", track_type="audio")

        selected = self.extractor._select_undefined_subtitle_track(
            [audio_track, ass_track]
        )

        self.assertIs(selected, ass_track)

    def test_undefined_ass_track_is_extracted_and_sent_for_translation(self):
        with TemporaryDirectory() as temp_directory:
            media_path = Path(temp_directory) / "episode.mkv"
            media_path.touch()
            raw_subtitle_path = Path(temp_directory) / "raw.ass"
            translated_path = Path(temp_directory) / "episode.kor.ass"

            def extract_subtitle():
                raw_subtitle_path.write_text("subtitle", encoding="utf-8")
                return str(raw_subtitle_path)

            ass_track = make_track("SubStationAlpha", "und")
            ass_track.extract = Mock(side_effect=extract_subtitle)

            env_configs = SimpleNamespace(
                MKV_SUBTITLE_EXTRACTION_LANGUAGE="kor",
                MKV_SUBTITLE_FALLBACK_LANGUAGE=["jpn", "eng"],
                ENABLE_SUBTITLE_TRANSLATION=True,
                _SUBTITLE_EXTENSIONS=["ass", "srt"],
            )
            extractor = MkvSubtitleExtractor(env_configs, LogExporter())
            translator = Mock()
            translator.translate_subtitle.return_value = str(translated_path)

            with (
                patch("src.analyzer.mkv_subtitle_extractor.MKVFile") as mkv_file_class,
                patch(
                    "src.translator.subtitle_translator.SubtitleTranslator",
                    return_value=translator,
                ),
            ):
                mkv_file_class.return_value.get_track.return_value = [ass_track]

                subtitles = extractor.extract_subtitle_file_from_mkv(
                    [File(str(media_path), FileType.MEDIA)], []
                )

            translator.translate_subtitle.assert_called_once()
            self.assertEqual(subtitles[0].get_absolute_path(), str(translated_path))


if __name__ == "__main__":
    unittest.main()
