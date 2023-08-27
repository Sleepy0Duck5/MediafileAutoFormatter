from src.constructor.constructor import Constructor


class Manager:
    def __init__(self, constructor: Constructor) -> None:
        self._constructor = constructor

    def process(self, source_path: str, target_path: str):
        struct = self._constructor.struct(source_path=source_path)
