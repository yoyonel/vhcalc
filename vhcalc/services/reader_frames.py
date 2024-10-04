import datetime
from io import BufferedReader
from pathlib import Path
from typing import Any, BinaryIO, Iterator, Tuple, Union

from imageio_ffmpeg import count_frames_and_secs, read_frames

from vhcalc.models import URL, MetaData
from vhcalc.tools.forked.imageio_ffmpeg_io import (
    read_frames_from_binary_stream,
    read_frames_from_url,
)
from vhcalc.tools.imghash import FRAME_SIZE


def build_reader_frames(
    media_input: Union[Path, Union[BufferedReader, BinaryIO], URL],
    nb_seconds_to_extract: float = 0,
    seek_to_middle: bool = False,
    ffmpeg_reduce_verbosity: bool = False,
) -> Tuple[Iterator[bytes], MetaData]:
    """

    Args:
        media_input:
        nb_seconds_to_extract:
        seek_to_middle:
        ffmpeg_reduce_verbosity:

    Returns:

    """
    ffmpeg_seek_input_cmd: list[str] = []
    ffmpeg_seek_output_cmd: list[str] = []
    s_media: str = ""

    # https://trac.ffmpeg.org/wiki/Seeking#Cuttingsmallsections
    if ffmpeg_reduce_verbosity:
        ffmpeg_seek_input_cmd += "-hide_banner -nostats -nostdin".split(" ")

    if isinstance(media_input, Path):
        s_media = str(media_input)
        # get media metadata from first yield of frames reader
        metadata_from_frames_reader: dict[str, Any] = next(read_frames(s_media))

        # extract a (frame's) chunk around/in middle of the media
        if seek_to_middle:
            # it's an approximation, this command seek around/close to the middle
            ffmpeg_seek_input_cmd += (
                "-ss",
                str(
                    datetime.timedelta(
                        seconds=metadata_from_frames_reader["duration"] // 2
                    )
                ),
            )

        if nb_seconds_to_extract:
            # express in number of frames to extract (more precise)
            ffmpeg_seek_output_cmd += (
                "-frames:v",
                str(round(nb_seconds_to_extract * metadata_from_frames_reader["fps"])),
            )

    # rescale output frame to 32x32
    video_filters = f"scale=width={FRAME_SIZE}:height={FRAME_SIZE}"

    if isinstance(media_input, Path):
        fn_read_frames = read_frames
    elif isinstance(media_input, BufferedReader):
        fn_read_frames = read_frames_from_binary_stream
    elif isinstance(media_input, URL):
        fn_read_frames = read_frames_from_url
    else:
        # TODO: handle this exception
        raise RuntimeError(f"Can't handle {type(media_input)=}")

    reader = fn_read_frames(
        media_input,
        pix_fmt="gray",
        input_params=[*ffmpeg_seek_input_cmd],
        output_params=[
            *ffmpeg_seek_output_cmd,
            *("-vf", video_filters),
        ],
        bits_per_pixel=8,
    )
    # get media metadata from first yield of reader
    metadata_from_frames_reader = next(reader)

    if isinstance(media_input, Path):
        nb_frames = count_frames_and_secs(s_media)[0]
    else:
        # FIXME: not accurate/exact => not working (very well)
        nb_frames = int(
            metadata_from_frames_reader["fps"] * metadata_from_frames_reader["duration"]
        )

    # build metadata dataclass
    metadata = MetaData(
        fps=metadata_from_frames_reader["fps"],
        duration=metadata_from_frames_reader["duration"],
        nb_frames=nb_frames,
    )

    return reader, metadata
