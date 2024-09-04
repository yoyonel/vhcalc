import datetime
from dataclasses import dataclass
from io import BufferedReader
from pathlib import Path
from typing import Any, Iterator, Tuple, Union

from imageio_ffmpeg import count_frames_and_secs, read_frames

from vhcalc.tools.forked.imageio_ffmpeg_io import read_frames_from_binary_stream
from vhcalc.tools.imghash import FRAME_SIZE


@dataclass
class MetaData:
    fps: float
    duration: float
    nb_frames: int


def build_reader_frames(
    media_input: Union[Path, BufferedReader],
    nb_seconds_to_extract: float = 0,
    seek_to_middle: bool = False,
    ffmpeg_reduce_verbosity: bool = True,
) -> Tuple[Iterator[bytes], MetaData]:
    ffmpeg_seek_input_cmd: list[str] = []
    ffmpeg_seek_output_cmd: list[str] = []
    s_media: str = ""
    nb_frames: int = 0

    # https://trac.ffmpeg.org/wiki/Seeking#Cuttingsmallsections
    if ffmpeg_reduce_verbosity:
        ffmpeg_seek_input_cmd += "-hide_banner -nostats -nostdin".split(" ")

    if isinstance(media_input, Path):
        s_media = str(media_input)
        meta: dict[str, Any] = next(read_frames(s_media))

        # extract a (frame's) chunk around/in middle of the media
        if seek_to_middle:
            # it's an approximation, this command seek around/close to the middle
            ffmpeg_seek_input_cmd += (
                "-ss",
                str(datetime.timedelta(seconds=meta["duration"] // 2)),
            )

        if nb_seconds_to_extract:
            # express in number of frames to extract (more precise)
            ffmpeg_seek_output_cmd += (
                "-frames:v",
                str(round(nb_seconds_to_extract * meta["fps"])),
            )

    # rescale output frame to 32x32
    video_filters = f"scale=width={FRAME_SIZE}:height={FRAME_SIZE}"

    if isinstance(media_input, Path):
        fn_read_frames = read_frames
        nb_frames = count_frames_and_secs(s_media)[0]
    elif isinstance(media_input, BufferedReader):
        fn_read_frames = read_frames_from_binary_stream
    else:
        # TODO: handle this exception
        raise RuntimeError(f"Can't handle {type(media_input)=}")

    reader = fn_read_frames(
        media_input,
        input_params=[*ffmpeg_seek_input_cmd],
        output_params=[
            *ffmpeg_seek_output_cmd,
            *("-vf", video_filters),
            *("-pix_fmt", "gray"),
        ],
        bits_per_pixel=8,
    )
    # yield metadata
    meta = next(reader)

    if not nb_frames:
        # FIXME: not accurate/exact => not working (very well)
        nb_frames = int(meta["fps"] * meta["duration"])

    # build metadata dataclass
    metadata = MetaData(
        fps=meta["fps"],
        duration=meta["duration"],
        nb_frames=nb_frames,
    )

    return reader, metadata
