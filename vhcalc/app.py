# -*- coding: utf-8 -*-
import pathlib
import sys
from importlib.metadata import version
from io import BufferedReader, BufferedWriter
from typing import Iterable, Optional

import rich_click as click
from loguru import logger

import vhcalc.services as services
from vhcalc.models.imghash_function import ImageHashingFunction
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
@click.option(
    "--image-hashing-method",
    type=click.Choice(ImageHashingFunction.names()),
    default="PerceptualHashing",
    show_default=True,
    # TODO: post validation and transform this option string to callable image hashing function
    # see: [Python Enum support for click.Choice #605](https://github.com/pallets/click/issues/605#issuecomment-901099036)
)
@click.option(
    "--decompress",
    # https://click.palletsprojects.com/en/8.1.x/options/#boolean-flags
    is_flag=True,
    type=bool,
    default=False,
    help="",
)
def imghash(
    input_stream: BufferedReader,
    output_stream: BufferedWriter,
    image_hashing_method: str,
    decompress: bool,
) -> None:
    """Simple form of the application: Input filepath > image hashes (to stdout by default)"""
    if decompress:
        for imghash_binary in services.a2b_imghash(input_stream):
            output_stream.write(str(imghash_binary).encode())
        return

    for frame_hash_binary in services.b2a_frames_to_imghash(
        input_stream,
        fn_imagehash=ImageHashingFunction[image_hashing_method],
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
