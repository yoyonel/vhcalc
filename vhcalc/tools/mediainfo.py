import platform
from typing import Any
from unittest.mock import Mock

from loguru import logger

MediaInfo: Any

try:
    from pymediainfo import MediaInfo as _MediaInfo

    # Check if library is available
    _MediaInfo._get_library()
    MediaInfo = _MediaInfo
except OSError:
    logger.error("Can't get library from pymediainfo.MediaInfo !", exc_info=True)
    if platform.system() != "Darwin":
        raise RuntimeError("Unexpected error occurred !") from None

    mock_MediaInfo = Mock()
    mock_MediaInfo.parse = Mock(return_value={})
    MediaInfo = mock_MediaInfo
