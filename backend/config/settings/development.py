from .base import *  # noqa: F403

DEBUG = True
# 10.0.2.2 is the Android emulator's alias for the host machine; without it the
# mobile app gets a DisallowedHost 400 before reaching any view.
ALLOWED_HOSTS = list({*ALLOWED_HOSTS, "testserver", "localhost", "127.0.0.1", "10.0.2.2"})

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
