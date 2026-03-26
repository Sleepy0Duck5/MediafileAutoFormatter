import os
import sys
import subprocess
from loguru import logger

from src.env_configs import EnvConfigs
from src.model.file import File


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
            logger.warning("TRANSLATION_SERVER_ADDRESS is not set. Skipping translation.")
            return subtitle_file.get_absolute_path()

        original_path = subtitle_file.get_absolute_path()
        file_ext = subtitle_file.get_extension()
        base_name = original_path[: -(len(file_ext) + 1)]
        output_path = f"{base_name}.kor.{file_ext}"

        args = ["llm-subtrans", "-l", "Korean", "-o", output_path]

        if self._env_configs.TRANSLATION_SERVER_ADDRESS:
            args.extend(["-s", self._env_configs.TRANSLATION_SERVER_ADDRESS])
        if self._env_configs.TRANSLATION_ENDPOINT:
            args.extend(["-e", self._env_configs.TRANSLATION_ENDPOINT])
        if self._env_configs.TRANSLATION_API_KEY:
            args.extend(["-k", self._env_configs.TRANSLATION_API_KEY])
        if self._env_configs.TRANSLATION_MODEL:
            args.extend(["--model", self._env_configs.TRANSLATION_MODEL])

        args.append(original_path)

        logger.info(f"Starting translation for {original_path} using llm-subtrans...")
        
        # Resolve llm-subtrans path in .venv/Scripts
        script_path = os.path.join(os.path.dirname(sys.executable), "llm-subtrans.exe")
        if not os.path.exists(script_path):
            script_path = os.path.join(os.path.dirname(sys.executable), "llm-subtrans")
        
        if os.path.exists(script_path):
            args[0] = script_path
        
        try:
            result = subprocess.run(args, capture_output=True, text=True, check=True)
            logger.info(f"Translation completed for {output_path}")
            return output_path
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to translate subtitle: {e.stderr}")
            return original_path
        except Exception as ex:
            logger.error(f"Failed to translate subtitle: {ex}")
            return original_path
