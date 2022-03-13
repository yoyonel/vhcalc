import datetime
from dataclasses import dataclass
from pathlib import Path
from typing import Iterator, Tuple

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
    meta = {}
    ffmpeg_seek_input_cmd = []
    ffmpeg_seek_output_cmd = []

    if ffmpeg_reduce_verbosity or seek_to_middle:
        meta = next(read_frames(str(media)))

    # extract a (frame's) chunk around/in middle of the media
    # https://trac.ffmpeg.org/wiki/Seeking#Cuttingsmallsections
    if ffmpeg_reduce_verbosity:
        ffmpeg_seek_input_cmd += "-hide_banner -nostats -nostdin".split(" ")

    if seek_to_middle:
        ffmpeg_seek_input_cmd += (
            f"-ss {str(datetime.timedelta(seconds=meta['duration'] // 2))}".split(" ")
        )

    if nb_seconds_to_extract:
        ffmpeg_seek_output_cmd += [
            "-frames:v",
            str(round(nb_seconds_to_extract * meta["fps"])),
        ]
    # rescale output frame to 32x32
    video_filters = f"scale=width={FRAME_SIZE}:height={FRAME_SIZE}"

    reader = read_frames(
        str(media),
        input_params=[*ffmpeg_seek_input_cmd],
        output_params=[
            *ffmpeg_seek_output_cmd,
            *f"-vf {video_filters}".split(" "),
            *"-pix_fmt gray".split(" "),
        ],
        bits_per_pixel=8,
    )
    meta = next(reader)
    metadata = MetaData(
        fps=meta["fps"],
        duration=meta["duration"],
        nb_frames=count_frames_and_secs(media)[0],
    )

    return reader, metadata
