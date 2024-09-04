from pathlib import Path

import pytest


@pytest.fixture
def test_data_dir():
    return Path(f"{Path(__file__).parent}/data")


@pytest.fixture()
def resource_video_path(test_data_dir):
    def _resource_video_path(video_filename: str):
        p_rvp = Path(f"{test_data_dir}/{video_filename}")
        assert p_rvp.exists()
        return p_rvp

    return _resource_video_path


@pytest.fixture()
def big_buck_bunny_trailer(resource_video_path) -> Path:
    """
    [ffmpeg via pipe: stream 1, offset 0x30: partial file](https://stackoverflow.com/questions/76479157/ffmpeg-via-pipe-stream-1-offset-0x30-partial-file)
    > *mp4* is compression mux type, then stream need can be seek, but stdin stream (*pipe:0*) can only read.
    > You must try another mux type like *flv*. And stdout stream(*pipe:1*) similar
    """
    return resource_video_path("big_buck_bunny_trailer_480p.mkv")
