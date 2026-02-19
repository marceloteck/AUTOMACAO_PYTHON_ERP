"""Logger de execução (arquivo + console)."""

from __future__ import annotations

import logging
from datetime import datetime
from pathlib import Path


class AppLogger:
    def __init__(self, native_logger: logging.Logger):
        self._logger = native_logger

    def info(self, message: str, *args) -> None:
        self._logger.info(message, *args)

    def warn(self, message: str, *args) -> None:
        self._logger.warning(message, *args)

    def error(self, message: str, *args) -> None:
        self._logger.error(message, *args)

    def exception(self, message: str, *args) -> None:
        self._logger.exception(message, *args)


def make_logger(log_dir: str) -> tuple[AppLogger, str]:
    base = Path(log_dir)
    base.mkdir(parents=True, exist_ok=True)

    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = base / f"run_{ts}.log"

    native = logging.getLogger(f"saa_corporate_{ts}")
    native.setLevel(logging.INFO)
    native.propagate = False
    native.handlers.clear()

    formatter = logging.Formatter("%(asctime)s | %(levelname)s | %(message)s")

    file_handler = logging.FileHandler(log_file, encoding="utf-8")
    file_handler.setFormatter(formatter)

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)

    native.addHandler(file_handler)
    native.addHandler(console_handler)

    return AppLogger(native), str(log_file)
