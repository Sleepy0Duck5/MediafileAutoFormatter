import argparse
from src.manager.manager import GeneralManager

if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument("source_path", type=str)
    parser.add_argument("target_path", type=str)

    args = parser.parse_args()

    print(args.source_path)
    print(args.target_path)

    manager = GeneralManager()
    manager.process(source_path=parser.source_path, target_path=parser.target_path)
