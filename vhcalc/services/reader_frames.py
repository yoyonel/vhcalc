import datetime
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterator, Tuple

from imageio_ffmpeg import count_frames_and_secs, read_frames

from vhcalc.tools.imghash import FRAME_SIZE


@dataclass
class MetaData:
    fps: float
    duration: float
    nb_frames: int


def build_reader_frames(
    media: Path,
    nb_seconds_to_extract: float = 0,
    seek_to_middle: bool = False,
    ffmpeg_reduce_verbosity: bool = True,
) -> Tuple[Iterator[bytes], MetaData]:
    s_media = str(media)
    meta: dict[str, Any] = next(read_frames(s_media))
    ffmpeg_seek_input_cmd: list[str] = []
    ffmpeg_seek_output_cmd: list[str] = []

    # extract a (frame's) chunk around/in middle of the media
    # https://trac.ffmpeg.org/wiki/Seeking#Cuttingsmallsections
    if ffmpeg_reduce_verbosity:
        ffmpeg_seek_input_cmd += "-hide_banner -nostats -nostdin".split(" ")

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

    reader = read_frames(
        s_media,
        input_params=[*ffmpeg_seek_input_cmd],
        output_params=[
            *ffmpeg_seek_output_cmd,
            *("-vf", video_filters),
            *("-pix_fmt", "gray"),
        ],
        bits_per_pixel=8,
    )
    # yield metadata
    next(reader)

    # build metadata dataclass
    metadata = MetaData(
        fps=meta["fps"],
        duration=meta["duration"],
        nb_frames=count_frames_and_secs(media)[0],
    )

    return reader, metadata
