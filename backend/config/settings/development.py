from .base import *  # noqa: F403

DEBUG = True
ALLOWED_HOSTS = list({*ALLOWED_HOSTS, "testserver", "localhost", "127.0.0.1"})
