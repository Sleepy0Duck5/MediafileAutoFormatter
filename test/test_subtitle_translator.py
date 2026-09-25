import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from types import SimpleNamespace
from unittest.mock import Mock, patch

from src.constants import FileType
from src.model.file import File
from src.translator.subtitle_translator import SubtitleTranslator


def make_env_configs():
    return SimpleNamespace(
        ENABLE_SUBTITLE_TRANSLATION=True,
        TRANSLATION_SERVER_ADDRESS="http://translation.test",
        TRANSLATION_TARGET_LANGUAGE="Korean",
        TRANSLATION_API_KEY="",
        TRANSLATION_ENDPOINT="/v1/chat/completions",
        TRANSLATION_MODEL="test-model",
    )


class SubtitleTranslatorTest(unittest.TestCase):
    def test_passes_new_llm_subtrans_options(self):
        with TemporaryDirectory() as temp_directory:
            source_path = Path(temp_directory) / "source.srt"
            source_path.write_text(
                "1\n00:00:01,000 --> 00:00:02,000\nHello\n",
                encoding="utf-8",
            )
            output_path = Path(temp_directory) / "source.ko.srt"
            output_path.write_text("translated", encoding="utf-8")

            project = Mock()
            project.subtitles.outputpath = str(output_path)
            project.use_project_file = False

            with (
                patch("scripts.subtrans_common.CreateOptions") as create_options,
                patch(
                    "scripts.subtrans_common.CreateProject", return_value=project
                ),
                patch("scripts.subtrans_common.LogTranslationStatus"),
                patch("PySubtrans.init_translator", return_value=Mock()),
            ):
                result = SubtitleTranslator(make_env_configs()).translate_subtitle(
                    File(str(source_path), FileType.SUBTITLE)
                )

            args = create_options.call_args.args[0]
            self.assertFalse(args.build_terminology_map)
            self.assertIsNone(args.terminology)
            self.assertIsNone(args.terminology_file)
            self.assertEqual(result, str(output_path))

    def test_propagates_translation_failure(self):
        with TemporaryDirectory() as temp_directory:
            source_path = Path(temp_directory) / "source.srt"
            source_path.touch()

            with patch(
                "scripts.subtrans_common.CreateOptions",
                side_effect=RuntimeError("translation failed"),
            ):
                with self.assertRaisesRegex(RuntimeError, "translation failed"):
                    SubtitleTranslator(make_env_configs()).translate_subtitle(
                        File(str(source_path), FileType.SUBTITLE)
                    )


if __name__ == "__main__":
    unittest.main()
