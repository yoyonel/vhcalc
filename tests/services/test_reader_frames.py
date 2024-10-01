# https://docs.python.org/3/library/typing.html#callable
from typing import Callable

import pytest

from vhcalc.models import URL, MetaData
from vhcalc.services.reader_frames import build_reader_frames


@pytest.mark.parametrize(
    "input_options,fn_expected_results",
    [
        # https://docs.pytest.org/en/6.2.x/example/parametrize.html#set-marks-or-test-id-for-individual-parametrized-test
        pytest.param(
            {}, lambda metadata_video: metadata_video.nb_frames, id="no options"
        ),
        pytest.param(
            {"seek_to_middle": True},
            lambda metadata_video: metadata_video.nb_frames // 2 + 6,
            id="seek to middle",
        ),
        pytest.param(
            {"nb_seconds_to_extract": 3},
            lambda metadata_video: round(metadata_video.fps) * 3,
            id="extract 3 seconds",
        ),
    ],
)
def test_build_reader_frames(
    input_options: dict,
    fn_expected_results: Callable[[MetaData], int],
    big_buck_bunny_trailer,
):
    p_video = big_buck_bunny_trailer
    gen_reader_frame, metadata_video = build_reader_frames(p_video, **input_options)
    # consume reader frames
    nb_frames_read = len(list(gen_reader_frame))
    nb_frames_expected = fn_expected_results(metadata_video)
    assert nb_frames_read == nb_frames_expected


def test_build_reader_frames_with_binary_stream_input(
    big_buck_bunny_trailer,
):
    p_video = big_buck_bunny_trailer
    gen_reader_frame, metadata_video = build_reader_frames(p_video.open("rb"))
    # consume reader frames
    nb_frames_read = len(list(gen_reader_frame))
    nb_frames_expected = metadata_video.nb_frames
    # FIXME: need to be more accurate
    assert abs(nb_frames_read - nb_frames_expected) <= int(metadata_video.fps)


def test_build_reader_frames_from_url(ftp_server_up):
    url = ftp_server_up
    try:
        gen_reader_frame, metadata = build_reader_frames(URL(url))
    except IOError:
        raise RuntimeError(
            "Can't extract metadata from url, maybe a problem with FFMPEG binary !"
        )
    print(metadata)
    nb_frames_read = len(list(gen_reader_frame))
    nb_frames_expected = metadata.nb_frames
    assert nb_frames_expected > 0
    # FIXME: need to be more accurate
    assert abs(nb_frames_read - nb_frames_expected) <= int(metadata.fps)
