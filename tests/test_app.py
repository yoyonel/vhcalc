import inspect
from importlib.metadata import version
from pathlib import Path
from tempfile import gettempdir

from vhcalc.app import cli, export_imghash_from_media
from vhcalc.services.imghashes import (
    export_imghash_from_media as svc_export_imghash_from_media,
)
from vhcalc.services.reader_frames import build_reader_frames


def get_default_parameters(func) -> dict:
    signature = inspect.signature(func)
    return {
        k: v.default
        for k, v in signature.parameters.items()
        if v.default is not inspect.Parameter.empty
    }


def assert_export_imghash_from_media_outputs(
    media: Path, binary_img_hash_file: Path, result_output: str
):
    _reader, metadata = build_reader_frames(media)

    default_chunk_nb_seconds = get_default_parameters(svc_export_imghash_from_media)[
        "chunk_nb_seconds"
    ]

    expected_outputs = (
        str(metadata),
        f"Number of frames to read: {int(metadata.nb_frames)}",
        f"Chunk size (nb frames): {int(default_chunk_nb_seconds * metadata.fps)}",
        f"output_file: {str(binary_img_hash_file)}",
        f"{media.name}",
    )
    result_output = result_output.replace("\n", "")
    for expected_output in expected_outputs:
        assert expected_output in result_output

    expected_size_binary_file = metadata.nb_frames * 8
    assert Path(binary_img_hash_file).stat().st_size == expected_size_binary_file


def test_cli_export_imghash(big_buck_bunny_trailer, cli_runner, tmpdir):
    p_video = big_buck_bunny_trailer
    resource_video_name = p_video.stem

    binary_img_hash_file = tmpdir.mkdir("phash") / f"{resource_video_name}.phash"

    result = cli_runner.invoke(
        export_imghash_from_media,
        args=f"-r {str(p_video)} -o {binary_img_hash_file}",
        catch_exceptions=False,
    )
    assert result.exit_code == 0

    assert_export_imghash_from_media_outputs(
        p_video, binary_img_hash_file, result.output
    )


def test_cli_export_imghash_without_export_file(big_buck_bunny_trailer, cli_runner):
    p_video = big_buck_bunny_trailer

    result = cli_runner.invoke(
        export_imghash_from_media,
        args=f"-r {str(p_video)}",
        catch_exceptions=False,
    )
    assert result.exit_code == 0

    _reader, metadata = build_reader_frames(p_video)

    expected_binary_img_hash_file = (
        Path(gettempdir()) / f"{p_video.name}.{metadata.fps}fps.phash"
    )

    assert_export_imghash_from_media_outputs(
        p_video, expected_binary_img_hash_file, result.output
    )


def test_cli_version(cli_runner):
    result = cli_runner.invoke(
        cli,
        args="--version",
        catch_exceptions=False,
    )
    assert result.exit_code == 0
    app_name_expected = "vhcalc"
    version_expected = version("vhcalc")
    assert f"{app_name_expected}, version {version_expected}\n" in result.output


def test_cli_imghash(big_buck_bunny_trailer, cli_runner, tmpdir):
    p_video = big_buck_bunny_trailer
    resource_video_name = p_video.stem

    binary_img_hash_file = tmpdir.mkdir("phash") / f"{resource_video_name}.phash"

    result = cli_runner.invoke(
        cli,
        args=f"{str(p_video)} {binary_img_hash_file}",
        catch_exceptions=False,
    )
    assert result.exit_code == 0
    assert not result.output

    _reader, metadata = build_reader_frames(p_video)
    expected_size_binary_file = metadata.nb_frames * 8
    assert Path(binary_img_hash_file).stat().st_size == expected_size_binary_file


def test_cli_imghash_without_export_file(big_buck_bunny_trailer, cli_runner):
    p_video = big_buck_bunny_trailer

    result = cli_runner.invoke(cli, args=str(p_video), catch_exceptions=False)
    assert result.exit_code == 0
    # TODO: catch stdout with binary images hashes
