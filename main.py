import argparse
from src.handler import Handler
from src.constructor.constructor import GeneralConstructor
from src.analyzer.media_type_analyzer import GeneralMediaTypeAnalyzer
from src.analyzer.media_analyzer_factory import MediaAnalyzerFactory
from src.analyzer.metadata_reader import GenearlMetadataReader
from src.restructor.restructor_factory import RestructorFactory
from src.executor.executor import GeneralExecutor
from src.env_configs import EnvConfigs

if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument("source_path", type=str)
    parser.add_argument("--target_path", type=str, default="", required=False)

    args = parser.parse_args()

    env_configs = EnvConfigs()

    print(args.source_path)
    print(args.target_path)

    handler = Handler(
        constructor=GeneralConstructor(env_configs=env_configs),
        media_type_analyzer=GeneralMediaTypeAnalyzer(
            env_configs=env_configs, metadata_reader=GenearlMetadataReader()
        ),
        media_analyzer_factory=MediaAnalyzerFactory(env_configs=env_configs),
        restructor_factory=RestructorFactory(env_configs=env_configs),
        executor=GeneralExecutor(),
    )

    handler.process(source_path=args.source_path, target_path=args.target_path)
