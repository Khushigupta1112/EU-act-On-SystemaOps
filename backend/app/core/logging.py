"""
Structured JSON logging configuration for SystemaOps.

Uses the standard library ``logging`` module with a JSON formatter so that
log lines can be ingested by log aggregation platforms (Datadog, CloudWatch,
OpenSearch, etc.) without additional parsing.

All log records include:
- timestamp (ISO-8601)
- level
- logger name
- message
- request_id (if set via contextvars)
- correlation_id (if set via contextvars)
- Any extra kwargs passed to the logger
"""

from __future__ import annotations

import json
import logging
import sys
from contextvars import ContextVar
from datetime import UTC, datetime
from typing import Any

# ---------------------------------------------------------------------------
# Context variables
# ---------------------------------------------------------------------------

request_id_var: ContextVar[str | None] = ContextVar("request_id", default=None)
correlation_id_var: ContextVar[str | None] = ContextVar("correlation_id", default=None)


# ---------------------------------------------------------------------------
# JSON formatter
# ---------------------------------------------------------------------------


class JsonFormatter(logging.Formatter):
    """Format log records as single-line JSON objects."""

    def format(self, record: logging.LogRecord) -> str:
        log_data: dict[str, Any] = {
            "timestamp": datetime.now(UTC).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "request_id": request_id_var.get(),
            "correlation_id": correlation_id_var.get(),
        }

        # Include any extra kwargs passed to the logger
        for key, value in record.__dict__.items():
            if key not in {
                "name", "msg", "args", "levelname", "levelno", "pathname",
                "filename", "module", "exc_info", "exc_text", "stack_info",
                "lineno", "funcName", "created", "msecs", "relativeCreated",
                "thread", "threadName", "processName", "process", "message",
                "taskName",
            }:
                log_data[key] = value

        # Append exception info if present
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)

        return json.dumps(log_data, default=str)


# ---------------------------------------------------------------------------
# Setup helper
# ---------------------------------------------------------------------------


def configure_logging(level: str = "INFO") -> None:
    """
    Configure the root logger to emit structured JSON to stdout.

    Call once at application startup (in ``app/main.py``).
    """
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(JsonFormatter())

    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, level.upper(), logging.INFO))
    root_logger.handlers.clear()
    root_logger.addHandler(handler)

    # Quiet noisy third-party loggers
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("httpx").setLevel(logging.WARNING)
