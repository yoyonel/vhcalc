import sys

# to prevent deprecated warning emit by pytest:
#   > DeprecationWarning: pkg_resources is deprecated as an API.
#   > See https://setuptools.pypa.io/en/latest/pkg_resources.html
# https://docs.python.org/3.9/library/importlib.metadata.html#distributions
from importlib.metadata import distribution

from imageio_ffmpeg import get_ffmpeg_version


def get_version_extended_informations() -> str:
    """

    Returns:
        str: String representation of the version extended information:
            - python version: python version interpreter
            - ffmpeg version: ffmpeg version binary (with some builds information like gcc version/platform)
            - for each "core" dependencies package: imagehash, numpy and Pillow
            => name and version package (using by the application)

    Example:
        The CLI option `version` get information from `get_version_extended_informations` function

        $ vhcalc --version
        vhcalc, version 0.4.0
        python version: 3.9.7 (default, Nov  7 2021, 10:52:45)
        [GCC 10.2.1 20210110]
        ffmpeg version 4.2.2-static
        ImageHash: 4.3.1
        numpy: 2.0.2
        pillow: 10.4.0
    """
    return "\n".join(
        (
            f"python version: {sys.version}",
            f"ffmpeg version {get_ffmpeg_version()}",
            "\n".join(
                f"{pkg_distro.name}: {pkg_distro.version}"  # type: ignore[attr-defined]
                for pkg_distro in map(distribution, ("imagehash", "numpy", "pillow"))
            ),
        )
    )
