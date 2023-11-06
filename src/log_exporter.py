import os
import traceback
import datetime

from loguru import logger


class LogExporter:
    def __init__(self) -> None:
        self._log = ""

    def export_traceback_as_file(self, source_path: str, target_path: str) -> None:
        try:
            log_path = source_path

            if not os.path.exists(log_path):
                os.makedirs(log_path)

            log_path = os.path.join(log_path, "MAF_Error.log")

            body = f"""Datetime : {datetime.datetime.now()}
Source Path : {source_path}
Target Path : {target_path}
Traceback : \n{traceback.format_exc()}
"""

            with open(log_path, "a+") as file:
                file.write(body)
                file.flush()

        except Exception as e:
            logger.opt(exception=e).error("Failed to export error log file")

    def append_log(self, message: str):
        self._log += message
