import argparse
from src.manager import Manager
from src.constructor.constructor import GeneralConstructor

if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument("source_path", type=str)
    parser.add_argument("--target_path", type=str, default="", required=False)

    args = parser.parse_args()

    print(args.source_path)
    print(args.target_path)

    manager = Manager(constructor=GeneralConstructor())
    manager.process(source_path=args.source_path, target_path=args.target_path)
