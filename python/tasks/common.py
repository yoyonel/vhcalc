import sys

VENV_PREFIX = "poetry run"
_COMMON_TARGETS = ["vhcalc", "tests"]
COMMON_TARGETS_AS_STR = " ".join(_COMMON_TARGETS)

# - [Add pty support for Windows? #561](https://github.com/pyinvoke/invoke/issues/561)
# - [invoke fails on windows #62](https://github.com/City-Bureau/city-scrapers/issues/62)
USE_PTY = sys.platform != "win32"
