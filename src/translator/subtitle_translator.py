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
        output_path = f"{base_name}.ko.{file_ext}"

        logger.info(f"Starting translation for {original_path} using llm-subtrans as a python module...")
        
        try:
            from scripts.subtrans_common import CreateOptions, CreateProject, LogTranslationStatus, InitLogger
            from PySubtrans import init_translator
            from argparse import Namespace
            
            project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            instruction_file_path = os.path.join(
                project_root, "resources", "translator", "instructions.txt"
            )
            
            args = Namespace(
                input=original_path,
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
                chat=True,             # Enable chat format for general APIs
                systemmessages=False,  
                auto=False,
                debug=False,
                list_formats=False
            )

            # InitLogger("llm-subtrans", args.debug)

            provider = "Custom Server" if args.server else "OpenRouter"
            
            if provider == "OpenRouter":
                options = CreateOptions(args, provider, api_key=args.apikey, model=args.model, use_default_model=args.auto)
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
            
            project.TranslateSubtitles(translator)
            
            if project.use_project_file:
                project.UpdateProjectFile()

            LogTranslationStatus(project, preview=args.preview)
            
            logger.info(f"Translation completed for {output_path}")
            
            gen_path = getattr(project.subtitles, 'outputpath', output_path)
            if gen_path and os.path.exists(gen_path):
                return gen_path
            elif os.path.exists(output_path):
                return output_path
                
            return original_path

        except Exception as ex:
            logger.error(f"Failed to translate subtitle: {ex}")
            return original_path
