from src.constructor.constructor import Constructor
from src.analyzer.media_type_analyzer import MediaTypeAnalyzer
from src.analyzer.media_analyzer_factory import MediaAnalyzerFactory
from src.restructor.restructor import Restructor
from src.executor.executor import Executor


class Handler:
    def __init__(
        self,
        constructor: Constructor,
        media_type_analyzer: MediaTypeAnalyzer,
        media_analyzer_factory: MediaAnalyzerFactory,
        restructor: Restructor,
        executor: Executor,
    ) -> None:
        self._constructor = constructor
        self._media_type_analyzer = media_type_analyzer
        self._media_analyzer_factory = media_analyzer_factory
        self._restructor = restructor
        self._executor = executor

    def process(self, source_path: str, target_path: str):
        root_folder = self._constructor.struct(source_path=source_path)

        media_type = self._media_type_analyzer.analyze(root=root_folder)

        media_analyzer = self._media_analyzer_factory.create(media_type=media_type)

        metadata = media_analyzer.analyze(root=root_folder)

        raise NotImplementedError

        restructed_folder = self._restructor.restruct(
            root=root_folder, metadata=metadata
        )

        self._executor.save(restructed_folder)
