import os
import sys
import subprocess
import tempfile
from loguru import logger

from src.env_configs import EnvConfigs
from src.model.file import File


ARIB_CAPTION_MARKERS = ("⚞", "⚟", "➡", "➨", "⤵")
JAPANESE_PUNCTUATION_REPLACEMENTS = {
    "。": ".",
    "、": ",",
    "，": ",",
    "．": ".",
    "！": "!",
    "？": "?",
    "：": ":",
    "；": ";",
    "（": "(",
    "）": ")",
    "～": "~",
}


class SubtitleTranslator:
    def __init__(self, env_configs: EnvConfigs) -> None:
        self._env_configs = env_configs

    def translate_subtitle(self, subtitle_file: File) -> str:
        """
        Translates a subtitle file using llm-subtrans and saves it as <filename>.kor.<ext>
        Returns the path to the translated subtitle file.
        """
        if not self._env_configs.ENABLE_SUBTITLE_TRANSLATION:
            logger.info("Subtitle translation is disabled.")
            return subtitle_file.get_absolute_path()

        if not self._env_configs.TRANSLATION_SERVER_ADDRESS:
            logger.warning(
                "TRANSLATION_SERVER_ADDRESS is not set. Skipping translation."
            )
            return subtitle_file.get_absolute_path()

        original_path = subtitle_file.get_absolute_path()
        file_ext = subtitle_file.get_extension()
        base_name = original_path[: -(len(file_ext) + 1)]
        output_path = f"{base_name}.ko.{file_ext}"

        logger.info(
            f"Starting translation for {original_path} using llm-subtrans as a python module..."
        )

        translation_input_path = original_path
        temporary_input_path = None

        try:
            translation_input_path, temporary_input_path = (
                self._create_sanitized_translation_input(
                    original_path=original_path,
                    file_ext=file_ext,
                )
            )

            from scripts.subtrans_common import (
                CreateOptions,
                CreateProject,
                LogTranslationStatus,
                InitLogger,
            )
            from PySubtrans import init_translator
            from argparse import Namespace

            project_root = os.path.dirname(
                os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            )
            instruction_file_path = os.path.join(
                project_root, "resources", "translator", "instructions.txt"
            )

            args = Namespace(
                input=translation_input_path,
                output=output_path,
                target_language=self._env_configs.TRANSLATION_TARGET_LANGUAGE,
                apikey=self._env_configs.TRANSLATION_API_KEY,
                server=self._env_configs.TRANSLATION_SERVER_ADDRESS,
                endpoint=self._env_configs.TRANSLATION_ENDPOINT,
                model=self._env_configs.TRANSLATION_MODEL,
                description=None,
                includeoriginal=False,
                addrtlmarkers=False,
                instruction=None,
                instructionfile=instruction_file_path,
                matchpartialwords=False,
                maxbatchsize=40,
                maxsummaries=None,
                maxlines=None,
                minbatchsize=5,
                moviename=None,
                name=None,
                names=None,
                postprocess=False,
                preprocess=False,
                project=False,
                preview=False,
                reparse=False,
                retranslate=False,
                reload=False,
                ratelimit=None,
                proxy=None,
                proxycert=None,
                scenethreshold=None,
                substitution=None,
                temperature=0.0,
                writebackup=False,
                chat=True,  # Enable chat format for general APIs
                systemmessages=False,
                auto=False,
                debug=False,
                list_formats=False,
                autosplit=False,
                build_terminology_map=False,
                terminology=None,
                terminology_file=None,
            )

            # InitLogger("llm-subtrans", args.debug)

            provider = "Custom Server" if args.server else "OpenRouter"

            if provider == "OpenRouter":
                options = CreateOptions(
                    args,
                    provider,
                    api_key=args.apikey,
                    model=args.model,
                    use_default_model=args.auto,
                )
            else:
                options = CreateOptions(
                    args,
                    provider,
                    api_key=args.apikey,
                    endpoint=args.endpoint,
                    model=args.model,
                    server_address=args.server,
                    supports_conversation=args.chat,
                    supports_system_messages=args.systemmessages,
                )

            project = CreateProject(options, args)
            translator = init_translator(options)

            self._translate_with_progress(project=project, translator=translator)

            if project.use_project_file:
                project.UpdateProjectFile()

            LogTranslationStatus(project, preview=args.preview)

            logger.info(f"Translation completed for {output_path}")

            gen_path = getattr(project.subtitles, "outputpath", output_path)
            if gen_path and os.path.exists(gen_path):
                translated_path = gen_path
            elif os.path.exists(output_path):
                translated_path = output_path
            else:
                return original_path

            self._normalize_translated_subtitle(translated_path)
            return translated_path

        except Exception as ex:
            logger.error(f"Failed to translate subtitle: {ex}")
            raise
        finally:
            if temporary_input_path and os.path.exists(temporary_input_path):
                os.remove(temporary_input_path)

    def _create_sanitized_translation_input(
        self, original_path: str, file_ext: str
    ) -> tuple[str, str | None]:
        """Create a temporary subtitle without ARIB caption control markers."""
        with open(original_path, "rb") as subtitle_file:
            original_content = subtitle_file.read()

        sanitized_content, change_count = self._normalize_subtitle_content(
            original_content
        )

        if change_count == 0:
            return original_path, None

        with tempfile.NamedTemporaryFile(
            mode="wb",
            prefix="subtitle-translation-",
            suffix=f".{file_ext}",
            delete=False,
        ) as temporary_file:
            temporary_file.write(sanitized_content)
            temporary_path = temporary_file.name

        logger.info(
            f"Applied {change_count} subtitle character normalizations to "
            "the temporary translation input"
        )
        return temporary_path, temporary_path

    def _normalize_translated_subtitle(self, translated_path: str) -> None:
        with open(translated_path, "rb") as subtitle_file:
            translated_content = subtitle_file.read()

        normalized_content, change_count = self._normalize_subtitle_content(
            translated_content,
            remove_arib_markers=False,
        )
        if change_count == 0:
            return

        with open(translated_path, "wb") as subtitle_file:
            subtitle_file.write(normalized_content)

        logger.info(
            f"Applied {change_count} Japanese punctuation normalizations to "
            f"the translated subtitle {translated_path}"
        )

    def _normalize_subtitle_content(
        self, content: bytes, remove_arib_markers: bool = True
    ) -> tuple[bytes, int]:
        normalized_content = content
        change_count = 0

        if remove_arib_markers:
            for marker in ARIB_CAPTION_MARKERS:
                encoded_marker = marker.encode("utf-8")
                marker_count = normalized_content.count(encoded_marker)
                change_count += marker_count
                normalized_content = normalized_content.replace(encoded_marker, b"")

        for source, replacement in JAPANESE_PUNCTUATION_REPLACEMENTS.items():
            encoded_source = source.encode("utf-8")
            replacement_count = normalized_content.count(encoded_source)
            change_count += replacement_count
            normalized_content = normalized_content.replace(
                encoded_source,
                replacement.encode("utf-8"),
            )

        return normalized_content, change_count

    def _translate_with_progress(self, project, translator) -> None:
        subtitles = project.subtitles
        total_lines = subtitles.linecount
        total_batches = sum(len(scene.batches) for scene in subtitles.scenes)
        processed_lines = 0

        logger.info(
            f"Translation prepared: {total_lines} lines in "
            f"{total_batches} batches across {subtitles.scenecount} scenes"
        )

        def log_batch_progress(sender, batch):
            nonlocal processed_lines
            processed_lines += batch.size
            percentage = 100 * processed_lines // total_lines if total_lines else 100

            token_message = ""
            if batch.translation:
                content = batch.translation.content
                prompt_tokens = content.get("prompt_tokens") or 0
                output_tokens = content.get("output_tokens") or 0
                if prompt_tokens or output_tokens:
                    token_message = (
                        f", tokens={prompt_tokens} input/{output_tokens} output"
                    )

            logger.info(
                f"Translation progress: batch {batch.scene}.{batch.number}, "
                f"{processed_lines}/{total_lines} lines ({percentage}%)"
                f"{token_message}"
            )

        def log_info(sender, message):
            logger.info(f"llm-subtrans: {message}")

        def log_warning(sender, message):
            logger.warning(f"llm-subtrans: {message}")

        def log_error(sender, message):
            logger.error(f"llm-subtrans: {message}")

        event_handlers = (
            (translator.events.batch_translated, log_batch_progress),
            (translator.events.info, log_info),
            (translator.events.warning, log_warning),
            (translator.events.error, log_error),
        )

        for signal, handler in event_handlers:
            signal.connect(handler, weak=False)

        try:
            project.TranslateSubtitles(translator)
        finally:
            for signal, handler in event_handlers:
                signal.disconnect(handler)
