# -*- coding: utf-8 -*-
import pathlib
import sys
from importlib.metadata import version
from io import BufferedReader, BufferedWriter
from typing import Iterable, Optional

import rich_click as click
from loguru import logger

import vhcalc.services as services
from vhcalc.tools.forked.click_default_group import DefaultGroup
from vhcalc.tools.forked.click_path import GlobPaths
from vhcalc.tools.version_extended_informations import get_version_extended_informations


@click.version_option(
    version=version("vhcalc"),
    prog_name="vhcalc",
    message=f"%(prog)s, version %(version)s\n{get_version_extended_informations()}",
)
@click.group(
    cls=DefaultGroup,
    default="imghash",
    default_if_no_args=True,
    invoke_without_command=True,
)
def cli() -> None:
    pass


@cli.command(
    short_help="Compute image hashes from and to binaries stream (by default: stdin/out)"
)
@click.argument("input_stream", type=click.File("rb"), default=sys.stdin.buffer)
@click.argument("output_stream", type=click.File("wb"), default=sys.stdout.buffer)
def imghash(input_stream: BufferedReader, output_stream: BufferedWriter) -> None:
    """Simple form of the application: Input filepath > image hashes (to stdout by default)"""
    for frame_hash_binary in services.compute_imghash_from_media_from_binary_stream(
        input_stream
    ):
        output_stream.write(frame_hash_binary)


@cli.command(
    short_help="extracting and exporting binary video hashes (fingerprints) from any video source"
)
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
    """Click entrypoint for extracting and exporting binary video hashes (fingerprints) from any video source"""
    for media in medias_pattern:
        services.export_imghash_from_media(media, output_file)


if __name__ == "__main__":
    cli()
