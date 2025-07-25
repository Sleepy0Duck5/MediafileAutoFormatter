import os
import traceback
import tempfile

from datetime import datetime
from loguru import logger
from typing import List

from src.constants import Constants, Extensions


class LogExporter:
    def __init__(self) -> None:
        self._logs: List[str] = []

    def export_traceback_as_file(self, source_path: str, target_path: str) -> None:
        try:
            log_path = source_path

            if not os.path.exists(log_path):
                os.makedirs(log_path)

            log_path = os.path.join(
                log_path, f"{Constants.ERROR_LOG_FILENAME}.{Extensions.LOG}"
            )

            body = f"""Datetime : {datetime.now()}
Source Path : {source_path}
Target Path : {target_path}
Traceback : \n{traceback.format_exc()}
"""

            with open(
                log_path,
                "a+",
            ) as file:
                file.write(body)
                file.flush()

            self._logs = []

        except Exception as e:
            logger.opt(exception=e).error("Failed to export error log file")

    def append_log(self, message: str, silent: bool = True):
        if not silent:
            if "warning" in message.lower():
                logger.warning(message)
            else:
                logger.info(message)

        self._logs.append(message + "\n")

    def export_log(self) -> str:
        log_file = tempfile.NamedTemporaryFile(delete=False)

        for log in self._logs:
            log_file.write(log.encode("utf-8"))
        log_file.flush()

        try:
            os.chmod(log_file.name, Constants.DEFAULT_PERMISSION_FOR_LOG_FILE)
        except Exception as e:
            logger.warning(
                f"Failed to grant permission {Constants.DEFAULT_PERMISSION_FOR_LOG_FILE} to {log_file.name}, error : {str(e)}"
            )

        return log_file.name

    def clear_log(self) -> None:
        self._logs = []
