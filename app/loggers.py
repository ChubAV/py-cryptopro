import logging
import logging.config
import logging.handlers
from pathlib import Path


def create_app_logger(debug: bool, log_dir: Path) -> logging.Logger:
    str_level = "DEBUG" if debug else "INFO"
    logging_config = {
        "version": 1,
        "formatters": {
            "format_for_console": {
                "format": (
                    "%(levelname)s: %(message)s: %(name)s: %(filename)s[%(funcName)s:%(lineno)d]"
                )
            },
            "format_for_file": {
                "format": (
                    "%(asctime)s: %(levelname)s: %(message)s: %(name)s: %(filename)s[%(funcName)s:%(lineno)d]"
                )
            },
        },
        "handlers": {
            "filelog": {
                "backupCount": 10,
                "class": "logging.handlers.RotatingFileHandler",
                "filename": Path(log_dir, "main.log").absolute(),
                "formatter": "format_for_file",
                "level": f"{str_level}",
                "maxBytes": 1000000,
            },
            "consolelog": {
                "class": "logging.StreamHandler",
                "formatter": "format_for_console",
                "level": f"{str_level}",
            },
        },
        # Specify all the subordinate loggers
        "loggers": {
            "crypto_pro_fast_api": {
                "handlers": ["consolelog", "filelog"],
                "level": f"{str_level}",
            },
            "": {"handlers": ["consolelog"], "level": f"{str_level}"},
        },
    }

    logging.config.dictConfig(logging_config)

    logger = logging.getLogger("crypto_pro_fast_api")

    return logger
