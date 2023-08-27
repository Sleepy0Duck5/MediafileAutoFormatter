from src.constructor.constructor import Constructor
from src.analyzer.analyzer import Analyzer
from src.restructor.restructor import Restructor
from src.executor.executor import Executor


class Manager:
    def __init__(
        self,
        constructor: Constructor,
        analyzer: Analyzer,
        restructor: Restructor,
        executor: Executor,
    ) -> None:
        self._constructor = constructor
        self._analyzer = analyzer
        self._restructor = restructor
        self._executor = executor

    def process(self, source_path: str, target_path: str):
        root_folder = self._constructor.struct(source_path=source_path)

        metadata = self._analyzer.analyze(root=root_folder)

        restructed_folder = self._restructor.restruct(
            root=root_folder, metadata=metadata
        )

        self._executor.save(restructed_folder)
