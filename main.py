from loguru import logger

from src.handler import Handler
from src.constructor.constructor import GeneralConstructor
from src.analyzer.media_type_analyzer import GeneralMediaTypeAnalyzer
from src.analyzer.media_analyzer_factory import MediaAnalyzerFactory
from src.analyzer.metadata_reader import GenearlMetadataReader
from src.restructor.restructor_factory import RestructorFactory
from src.restructor.subtitle_extractor import GeneralSubtitleExtractor
from src.log_exporter import LogExporter
from src.executor.executor import GeneralExecutor
from src.env_configs import EnvConfigs
from src.constants import Log
from src.arguments import ArgumentParser


if __name__ == "__main__":
    logger.info("Mediafile Auto Formatter started")

    arguments = ArgumentParser().get_arguments()

    env_configs = EnvConfigs()

    if env_configs._EXPORT_DEBUG_LOG_FILE:
        logger.add(Log.LOG_FILE_NAME, rotation=Log.LOG_FILE_ROTATION)

    constructor = GeneralConstructor(env_configs=env_configs)
    log_exporter = LogExporter()

    handler = Handler(
        constructor=constructor,
        media_type_analyzer=GeneralMediaTypeAnalyzer(
            env_configs=env_configs, metadata_reader=GenearlMetadataReader()
        ),
        media_analyzer_factory=MediaAnalyzerFactory(env_configs=env_configs),
        restructor_factory=RestructorFactory(
            env_configs=env_configs,
            subtitle_extractor=GeneralSubtitleExtractor(constrcutor=constructor),
            arguments=arguments,
        ),
        executor=GeneralExecutor(log_exporter=log_exporter),
        log_exporter=log_exporter,
    )

    handler.process(
        arguments=arguments,
    )
