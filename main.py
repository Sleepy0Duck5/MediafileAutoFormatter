import argparse
from loguru import logger

from src.handler import Handler
from src.constructor.constructor import GeneralConstructor
from src.analyzer.media_type_analyzer import GeneralMediaTypeAnalyzer
from src.analyzer.media_analyzer_factory import MediaAnalyzerFactory
from src.analyzer.metadata_reader import GenearlMetadataReader
from src.restructor.restructor_factory import RestructorFactory
from src.restructor.subtitle_extractor import GeneralSubtitleExtractor
from src.executor.executor import GeneralExecutor
from src.env_configs import EnvConfigs
from src.constants import Constants


def _init_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()

    parser.add_argument("source_path", type=str)
    parser.add_argument("--target_path", type=str, default="", required=False)

    return parser


if __name__ == "__main__":
    args = _init_parser().parse_args()

    env_configs = EnvConfigs()

    logger.info(args.source_path)
    logger.info(args.target_path)

    constructor = GeneralConstructor(env_configs=env_configs)

    logger.add(Constants.LOG_FILE_NAME)

    handler = Handler(
        constructor=constructor,
        media_type_analyzer=GeneralMediaTypeAnalyzer(
            env_configs=env_configs, metadata_reader=GenearlMetadataReader()
        ),
        media_analyzer_factory=MediaAnalyzerFactory(env_configs=env_configs),
        restructor_factory=RestructorFactory(
            env_configs=env_configs,
            subtitle_extractor=GeneralSubtitleExtractor(constrcutor=constructor),
        ),
        executor=GeneralExecutor(),
    )

    handler.process(source_path=args.source_path, target_path=args.target_path)
