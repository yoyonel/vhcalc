from pathlib import Path

import pytest


@pytest.fixture(scope="session")
def test_data_dir():
    return Path(f"{Path(__file__).parent}/data")


@pytest.fixture(scope="session")
def resource_video_path(test_data_dir):
    def _resource_video_path(video_filename: str):
        p_rvp = Path(f"{test_data_dir}/{video_filename}")
        assert p_rvp.exists()
        return p_rvp

    return _resource_video_path


@pytest.fixture(scope="session")
def big_buck_bunny_trailer(resource_video_path) -> Path:
    """
    [ffmpeg via pipe: stream 1, offset 0x30: partial file](https://stackoverflow.com/questions/76479157/ffmpeg-via-pipe-stream-1-offset-0x30-partial-file)
    > *mp4* is compression mux type, then stream need can seek, but stdin stream (*pipe:0*) can only read.
    > You must try another mux type like *flv*. And stdout stream(*pipe:1*) similar
    """
    return resource_video_path("big_buck_bunny_trailer_480p.mkv")


@pytest.fixture(scope="session", autouse=True)
def ftp_server_up(ftpserver, big_buck_bunny_trailer):
    file_uploaded = ftpserver.put_files(
        str(big_buck_bunny_trailer), style="url", anon=True
    )
    assert len(file_uploaded) == 1
    return file_uploaded[0]
