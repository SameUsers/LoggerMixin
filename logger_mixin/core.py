import os
import logging
from pathlib import Path
from logging.handlers import RotatingFileHandler
from datetime import datetime, timezone

class MetaLogger(type):
    def __new__(mcs, name, bases, namespace) -> type:
        namespace.setdefault("LOG_DIR",Path(os.getenv("LOG_DIR", "logs")))
        if "LOG_LEVEL" not in namespace:
            level_name = os.getenv("LOG_LEVEL", "DEBUG").upper()
            level = logging.getLevelNamesMapping().get(level_name)
            if level is None:
                raise ValueError(f"Invalid LOG_LEVEL: {level_name}")
            namespace["LOG_LEVEL"] = level
        return super().__new__(mcs, name, bases, namespace)


class LoggerMixin(metaclass=MetaLogger):
    LOG_DIR: Path
    LOG_LEVEL: int

    def __init__(self, logger_name: str|None = None, name_by_date: bool = False) -> None:
        if logger_name is not None and name_by_date:
            raise RuntimeError(
                "Параметры logger_name и name_by_date=True являются взаимоисключающими. "
                "Укажите имя логгера либо включите автоматическое формирование имени по дате."
            )
        self._logger_name = (
            datetime.now(tz=timezone.utc).strftime("%Y-%m-%d_%H-%M-%S_%f")
            if name_by_date
            else logger_name or f"{self.__class__.__module__}.{self.__class__.__qualname__}"
        )
        self._logger = logging.getLogger(self._logger_name)
        self._additional_logger: dict[str, logging.Logger] = dict()
        self._setup_logger()

    def append_stream_logger(self, name: str) -> None:
        if name in self._additional_logger:
            return
        logger = logging.getLogger(name)
        self._set_logger_level(logger, self.LOG_LEVEL)
        if not logger.handlers:
            handler = logging.StreamHandler()
            self._set_logger_formatter(handler)
            self._add_handlers(logger, [handler])
        self._additional_logger[name] = logger

    def append_file_logger(self, name: str) -> None:
        if name in self._additional_logger:
            return
        logger = logging.getLogger(name)
        self._set_logger_level(logger, self.LOG_LEVEL)
        log_dir = self.LOG_DIR / self.__class__.__name__
        log_dir.mkdir(parents=True, exist_ok=True)
        if not logger.handlers:
            filename = self._replace_delimiters(name)
            handler = RotatingFileHandler(
                filename=log_dir / f"{filename}.log",
                maxBytes=10 * 1024 * 1024,
                backupCount=5,
                encoding="utf-8",
            )
            self._set_logger_formatter(handler)
            self._add_handlers(logger, handlers=[handler])
        self._additional_logger[name] = logger

    def _set_logger_level(self, logger: logging.Logger, level: int) -> None:
        logger.setLevel(level)

    def _set_logger_formatter(self,handler: logging.Handler) -> None:
        handler.setFormatter(logging.Formatter(fmt="%(asctime)s | %(levelname)s | %(name)s | %(message)s", datefmt="%Y-%m-%d %H:%M:%S"))

    def _add_handlers(self, logger: logging.Logger, handlers: list[logging.Handler]) -> None:
        for handler in handlers:
            logger.addHandler(handler)
        logger.propagate = False

    def _replace_delimiters(self, name: str) -> str:
        return name.replace("/", "_").replace("\\", "_")

    def _setup_logger(self) -> None:
        _log_dir = self.LOG_DIR / f"{self.__class__.__name__}"
        _log_dir.mkdir(parents=True, exist_ok=True)
        self._set_logger_level(self._logger, self.LOG_LEVEL)
        if self._logger.handlers:
            return
        filename = self._replace_delimiters(self._logger_name)
        file_handler = RotatingFileHandler(
            filename=_log_dir / f"{filename}.log",
            maxBytes=10 * 1024 * 1024,
            backupCount=5,
            encoding="utf-8",
        )
        console_handler = logging.StreamHandler()
        handlers = [file_handler, console_handler]
        for handler in handlers:
            self._set_logger_formatter(handler)
        self._add_handlers(self._logger, handlers)

    @property
    def logger(self) -> logging.Logger:
        return self._logger

    @property
    def additional_logger(self) -> dict[str, logging.Logger]:
        return self._additional_logger
