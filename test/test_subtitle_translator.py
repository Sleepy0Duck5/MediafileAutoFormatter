import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from types import SimpleNamespace
from unittest.mock import Mock, patch

from blinker import Signal

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
            project.subtitles = SimpleNamespace(
                outputpath=str(output_path),
                linecount=1,
                scenecount=1,
                scenes=[SimpleNamespace(batches=[])],
            )
            project.use_project_file = False
            translator = SimpleNamespace(
                events=SimpleNamespace(
                    batch_translated=Signal(),
                    info=Signal(),
                    warning=Signal(),
                    error=Signal(),
                )
            )

            with (
                patch("scripts.subtrans_common.CreateOptions") as create_options,
                patch("scripts.subtrans_common.CreateProject", return_value=project),
                patch("scripts.subtrans_common.LogTranslationStatus"),
                patch("PySubtrans.init_translator", return_value=translator),
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

    def test_logs_batch_progress(self):
        events = SimpleNamespace(
            batch_translated=Signal(),
            info=Signal(),
            warning=Signal(),
            error=Signal(),
        )
        translator = SimpleNamespace(events=events)
        batch = SimpleNamespace(
            scene=1,
            number=1,
            size=4,
            translation=SimpleNamespace(
                content={"prompt_tokens": 120, "output_tokens": 80}
            ),
        )
        scene = SimpleNamespace(batches=[batch, SimpleNamespace()])
        project = SimpleNamespace(
            subtitles=SimpleNamespace(
                linecount=10,
                scenecount=1,
                scenes=[scene],
            )
        )

        def translate_subtitles(active_translator):
            active_translator.events.info.send(
                active_translator, message="Translating 10 lines"
            )
            active_translator.events.batch_translated.send(
                active_translator, batch=batch
            )

        project.TranslateSubtitles = Mock(side_effect=translate_subtitles)

        with patch("src.translator.subtitle_translator.logger") as test_logger:
            SubtitleTranslator(make_env_configs())._translate_with_progress(
                project=project,
                translator=translator,
            )

        messages = [call.args[0] for call in test_logger.info.call_args_list]
        self.assertTrue(
            any(
                "10 lines in 2 batches across 1 scenes" in message
                for message in messages
            )
        )
        self.assertTrue(
            any(
                "4/10 lines (40%), tokens=120 input/80 output" in message
                for message in messages
            )
        )


if __name__ == "__main__":
    unittest.main()
