from loguru import logger

from src.constructor.constructor import Constructor
from src.analyzer.media_type_analyzer import MediaTypeAnalyzer
from src.analyzer.media_analyzer_factory import MediaAnalyzerFactory
from src.restructor.restructor_factory import RestructorFactory
from src.executor.executor import Executor


class Handler:
    def __init__(
        self,
        constructor: Constructor,
        media_type_analyzer: MediaTypeAnalyzer,
        media_analyzer_factory: MediaAnalyzerFactory,
        restructor_factory: RestructorFactory,
        executor: Executor,
    ) -> None:
        self._constructor = constructor
        self._media_type_analyzer = media_type_analyzer
        self._media_analyzer_factory = media_analyzer_factory
        self._restructor_factory = restructor_factory
        self._executor = executor

    def process(self, source_path: str, target_path: str):
        try:
            root_folder = self._constructor.struct(source_path=source_path)

            media_type = self._media_type_analyzer.analyze(root=root_folder)

            metadata = self._media_analyzer_factory.create(
                media_type=media_type
            ).analyze(root=root_folder)

            restructed_folder = self._restructor_factory.create(
                media_type=media_type
            ).restruct(metadata=metadata, target_path=target_path)

            raise NotImplementedError("WIP")

            self._executor.execute(restructed_folder)

        except Exception as e:
            logger.error(e)
            raise e
