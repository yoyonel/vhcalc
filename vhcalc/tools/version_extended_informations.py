import sys

import pkg_resources
from imageio_ffmpeg import get_ffmpeg_version


def get_version_extended_informations() -> str:
    return "\n".join(
        (
            f"python version: {sys.version}",
            "\n".join(
                f"{pkg_distribution.project_name}: {pkg_distribution.version}"
                for pkg_distribution in map(
                    pkg_resources.get_distribution, ("imagehash", "numpy", "pillow")
                )
            ),
            f"ffmpeg version {get_ffmpeg_version()}",
        )
    )
