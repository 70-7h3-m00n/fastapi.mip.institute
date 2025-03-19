import re
from logging import Formatter, Logger, LogRecord
from logging.config import dictConfig
from typing import Any, Generator, Iterable
import logging
import sys

from app.config import config
from app.utils import json_dumps

DEFAULT_FIELDS = (
    "%(levelname)s",
    "%(name).256s",
    "%(lineno)d",
    "%(message).256s",
    "%(stack_trace).768s",
)


class LimitList:
    def __init__(self) -> None:
        self._parts: list[str] = []

    def append(self, part: str, limit: int) -> int:
        length = len(part) + 1
        if length > limit:
            return 0

        self._parts.append(part)
        return limit - length

    def __iter__(self) -> Generator[str, None, None]:
        yield from self._parts

    def __len__(self) -> int:
        return len(self._parts)


class StackCropper:
    DELIMITER = "\n...\n\n"

    def __init__(self, traceback: str, limit: int) -> None:
        self._traceback = traceback
        self._limit = limit
        self._current_limit = limit
        self._first = LimitList()
        self._last = LimitList()

    def crop(self) -> str:
        if self._limit == 0:
            return ""

        if len(self._traceback) < self._limit:
            return self._traceback

        self._limit -= len(self.DELIMITER) + 1
        splitted = self._traceback.split("\n")
        cropped = self._split(splitted)
        return "\n".join(cropped)

    def _split(self, splitted: list[str]) -> Iterable[str]:
        idx = 0
        while idx < len(splitted) // 2 and self._limit:
            first = splitted[idx]
            last = splitted[-(idx + 1)]
            self._limit = self._first.append(first, self._limit)
            self._limit = self._last.append(last, self._limit)
            idx += 1

        if not self._first or not self._last:
            return ""

        yield from self._first
        yield self.DELIMITER
        yield from reversed(list(self._last))


class JsonFormatter(Formatter):
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self._required_fields = self._get_required_fields()

    def format(self, record: LogRecord) -> str:  # noqa: WPS125
        if "asctime" in self._required_fields:
            record.asctime = self.formatTime(record, self.datefmt)
        log_record = self._create_log_record(record)
        return json_dumps(log_record, decode=True)

    def _convert(self, record: LogRecord, field: str, size: int | None = None) -> Any:
        field_value = getattr(record, field, "")
        if not field_value or not size:
            return field_value
        if not isinstance(field_value, str) or len(field_value) <= size:
            return field_value
        cropped = field_value[:size]
        return f"{cropped}.."

    def _get_required_fields(self) -> dict[str, Any]:
        if not self._fmt:
            self._fmt = " ".join(DEFAULT_FIELDS)
        standard_formatters = re.compile(r"\((.+?)\)(?:\.(\d*)s)?", re.IGNORECASE)
        fields = standard_formatters.findall(self._fmt)
        return {field: int(value) if value else None for field, value in fields}

    def _create_log_record(self, record: LogRecord) -> dict[str, Any]:
        log_record = {}
        record.message = record.getMessage()
        log_record.update(
            {
                field: self._convert(record, field, size)
                for field, size in self._required_fields.items()
            }
        )
        log_record.update(self._get_exception(record))
        return log_record

    def _get_exception(self, record: LogRecord) -> dict[str, Any]:
        if not record.exc_info:
            return {}
        size = self._required_fields.get("stack_trace")
        if not size:
            size = 768
        cropper = StackCropper(self.formatException(record.exc_info), size)
        return {"stack_trace": cropper.crop()}


def setup_logging() -> None:
    dictConfig(config.logging.config)


def get_logger() -> Logger:
    logger = logging.getLogger("app")
    # Only configure if not already configured
    if not logger.handlers:
        logger.setLevel(logging.INFO)
        # Create console handler with a higher log level
        handler = logging.StreamHandler(sys.stdout)  # Explicitly use stdout
        handler.setLevel(logging.INFO)
        # Create formatter
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        # Add the handler to the logger
        logger.addHandler(handler)
        # Ensure propagation is enabled
        logger.propagate = True
    return logger
