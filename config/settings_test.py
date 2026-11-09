"""Settings used by the test suite."""

import os

os.environ.setdefault("DJANGO_DEBUG", "1")

from .settings import *  # noqa: E402,F403
