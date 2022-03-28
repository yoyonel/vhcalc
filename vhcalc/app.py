# -*- coding: utf-8 -*-
import pathlib
from importlib.metadata import version
from typing import Iterable, Optional

import click
from click_path import GlobPaths
from loguru import logger

import vhcalc.services as services


@click.command(
    short_help="extracting and exporting binary video hashes (fingerprints) from any video source"
)
@click.version_option(version=version(__package__ or __name__))
@click.option(
    "--medias_pattern",
    "-r",
    required=True,
    type=GlobPaths(
        files_okay=True,
        dirs_okay=False,
        readable_only=True,
        at_least_one=True,
    ),
    help="Pattern to find medias",
)
@click.option(
    "--output-file",
    "-o",
    default=None,
    type=click.Path(writable=True, path_type=pathlib.Path),
    help="File where to write images hashes.",
)
@logger.catch
def export_imghash_from_media(
    medias_pattern: Iterable[pathlib.Path], output_file: Optional[pathlib.Path]
) -> None:
    """This script exporting binary images hashes (fingerprints)
    from (any) media (video file)
    \f"""
    for media in medias_pattern:
        services.export_imghash_from_media(media, output_file)
