# -*- coding: utf-8 -*-
import pathlib
from importlib.metadata import version
from typing import Optional

import click
from loguru import logger

import vhcalc.services as services


@click.command(
    short_help="extracting and exporting binary video hashes (fingerprints) from any video source"
)
@click.version_option(version=version(__package__ or __name__))
@click.option(
    "--media",
    "-r",
    required=True,
    type=click.Path(
        exists=True,
        readable=True,
        resolve_path=True,
        allow_dash=False,
        path_type=pathlib.Path,
    ),
    help="Path to media",
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
    media: pathlib.Path, output_file: Optional[pathlib.Path]
) -> None:
    """This script exporting binary images hashes (fingerprints)
    from (any) media (video file)
    \f"""
    services.export_imghash_from_media(media, output_file)
