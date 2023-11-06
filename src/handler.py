import os
from loguru import logger

from src.errors import DirectoryNotFoundException
from src.constructor.constructor import Constructor
from src.analyzer.media_type_analyzer import MediaTypeAnalyzer
from src.analyzer.media_analyzer_factory import MediaAnalyzerFactory
from src.restructor.restructor_factory import RestructorFactory
from src.executor.executor import Executor
from src.log_exporter import LogExporter


class Handler:
    def __init__(
        self,
        constructor: Constructor,
        media_type_analyzer: MediaTypeAnalyzer,
        media_analyzer_factory: MediaAnalyzerFactory,
        restructor_factory: RestructorFactory,
        executor: Executor,
        log_exporter: LogExporter,
    ) -> None:
        self._constructor = constructor
        self._media_type_analyzer = media_type_analyzer
        self._media_analyzer_factory = media_analyzer_factory
        self._restructor_factory = restructor_factory
        self._executor = executor
        self._log_exporter = log_exporter

    def process(
        self, source_path: str, target_path: str, multiple: bool = False
    ) -> None:
        try:
            if not os.path.exists(source_path):
                raise DirectoryNotFoundException

            if not multiple:
                self._process(source_path=source_path, target_path=target_path)
                return

            childs = next(os.walk(source_path))
            child_directories = childs[1]

            for child_name in child_directories:
                child_path = os.path.join(source_path, child_name)
                self._process(source_path=child_path, target_path=target_path)

        except Exception as e:
            logger.opt(exception=e).error(e)
            self._log_exporter.export_traceback_as_file(
                source_path=source_path, target_path=target_path
            )

    def _process(self, source_path: str, target_path: str) -> None:
        try:
            root_folder = self._constructor.struct(source_path=source_path)

            media_type = self._media_type_analyzer.analyze(root=root_folder)

            metadata = self._media_analyzer_factory.create(
                media_type=media_type
            ).analyze(root=root_folder)

            restructed_folder = self._restructor_factory.create(
                media_type=media_type
            ).restruct(metadata=metadata, target_path=target_path)

            self._executor.execute(new_root_folder=restructed_folder, metadata=metadata)

        except Exception as e:
            logger.opt(exception=e).error(e)
            self._log_exporter.export_traceback_as_file(
                source_path=source_path, target_path=target_path
            )
