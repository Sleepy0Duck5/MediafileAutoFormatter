import argparse
from src.manager import Manager
from src.constructor.constructor import GeneralConstructor
from src.analyzer.analyzer import GeneralAnalyzer
from src.analyzer.metadata_reader import GenearlMetadataReader
from src.restructor.restructor import GeneralRestructor
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

    manager = Manager(
        constructor=GeneralConstructor(env_configs=env_configs),
        analyzer=GeneralAnalyzer(
            env_configs=env_configs, metadata_reader=GenearlMetadataReader()
        ),
        restructor=GeneralRestructor(),
        executor=GeneralExecutor(),
    )
    manager.process(source_path=args.source_path, target_path=args.target_path)
