from .base import *  # noqa: F403

DEBUG = True
ALLOWED_HOSTS = ["testserver", "localhost", "127.0.0.1"]
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": ":memory:",
    }
}

# Test-specific settings
PASSWORD_HASHERS = [
    "django.contrib.auth.hashers.MD5PasswordHasher",
]

# DRF throttles are keyed on client IP and backed by the default LocMemCache,
# which survives across tests in one process. Left enabled, every test after the
# burst limit would see a 429 instead of exercising the real code path. A rate of
# None disables that scope. Tests that assert throttling override this locally.
REST_FRAMEWORK = {
    **REST_FRAMEWORK,  # noqa: F405
    "DEFAULT_THROTTLE_RATES": {
        "forgot_password_burst": None,
        "forgot_password_daily": None,
        "login": None,
    },
}

# Disable logging during tests
LOGGING = {
    "version": 1,
    "disable_existing_loggers": True,
}
