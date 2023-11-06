import os
import traceback

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

            self._executor.execute(new_root_folder=restructed_folder, metadata=metadata)

        except Exception as e:
            logger.opt(exception=e).error(e)
            self._export_log_as_file(source_path=source_path, target_path=target_path)

    def _export_log_as_file(self, source_path: str, target_path: str) -> None:
        try:
            title = source_path.split(os.sep)[-1]
            log_path = os.path.join(target_path, title)

            if not os.path.exists(log_path):
                os.makedirs(log_path)

            log_path = os.path.join(log_path, "MAF_Exception.log")

            body = f"""Source Path : {source_path}
Target Path : {target_path}
Traceback : \n{traceback.format_exc()}"""

            with open(log_path, "w+") as file:
                file.write(body)
                file.flush()

        except Exception as e:
            logger.opt(exception=e).error("Failed to export error log file")
