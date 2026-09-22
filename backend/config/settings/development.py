from .base import *  # noqa: F403

DEBUG = True
ALLOWED_HOSTS = list({*ALLOWED_HOSTS, "testserver", "localhost", "127.0.0.1"})

# Development-specific settings
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
        },
    },
    "root": {
        "handlers": ["console"],
        "level": "INFO",
    },
    "loggers": {
        "django": {
            "handlers": ["console"],
            "level": "INFO",
            "propagate": False,
        },
    },
}
