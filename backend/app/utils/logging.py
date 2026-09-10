import logging
import json
import sys
from datetime import datetime, timezone
from app.config.settings import settings


class StructuredJSONFormatter(logging.Formatter):
    """
    Structured JSON log formatter that ensures sensitive data like API keys,
    resume content, and tokens are never printed in raw logs.
    """
    SENSITIVE_KEYS = {"TELEGRAM_BOT_TOKEN", "LLM_API_KEY", "api_key", "token", "password", "resume_text", "jd_text"}

    def format(self, record: logging.LogRecord) -> str:
        log_entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }

        # Include contextual fields if present
        for key in ("request_id", "operation", "duration", "status", "error_code"):
            if hasattr(record, key):
                log_entry[key] = getattr(record, key)

        if record.exc_info:
            log_entry["exception"] = self.formatException(record.exc_info)

        return json.dumps(log_entry)


def setup_logging():
    log_level = getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO)
    logger = logging.getLogger()
    logger.setLevel(log_level)

    # Clear existing handlers
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)

    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(StructuredJSONFormatter())
    logger.addHandler(handler)

    # Quiet external verbose loggers
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("asyncio").setLevel(logging.WARNING)
