import inspect
import json
from importlib.metadata import version
from pathlib import Path, PureWindowsPath
from tempfile import gettempdir

from flatten_dict import flatten

from vhcalc.app import cli, export_imghash_from_media, mediainfo
from vhcalc.services.imghashes import (
    export_imghash_from_media as svc_export_imghash_from_media,
)
from vhcalc.services.reader_frames import build_reader_frames


def stringify_path(p: Path) -> str:
    return p.as_posix() if isinstance(p, PureWindowsPath) else str(p)


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

    binary_img_hash_file = Path(tmpdir.mkdir("phash") / f"{resource_video_name}.phash")

    result = cli_runner.invoke(
        export_imghash_from_media,
        args=f"-r {stringify_path(p_video)} -o {stringify_path(binary_img_hash_file)}",
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
        args=f"-r {stringify_path(p_video)}",
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

    binary_img_hash_file = Path(tmpdir.mkdir("phash") / f"{resource_video_name}.phash")

    result = cli_runner.invoke(
        cli,
        args=f"{stringify_path(p_video)} {stringify_path(binary_img_hash_file)}",
        catch_exceptions=False,
    )
    assert result.exit_code == 0
    assert not result.output

    _reader, metadata = build_reader_frames(p_video)
    expected_size_binary_file = metadata.nb_frames * 8
    assert Path(binary_img_hash_file).stat().st_size == expected_size_binary_file

    result = cli_runner.invoke(
        cli,
        args=f"--decompress {stringify_path(binary_img_hash_file)}",
        catch_exceptions=False,
    )
    assert result.exit_code == 0


def test_cli_imghash_without_export_file(big_buck_bunny_trailer, cli_runner):
    p_video = big_buck_bunny_trailer

    result = cli_runner.invoke(
        cli, args=stringify_path(p_video), catch_exceptions=False
    )
    assert result.exit_code == 0
    # TODO: catch stdout with binary images hashes


def test_cli_mediainfo(big_buck_bunny_trailer, cli_runner):
    p_video = big_buck_bunny_trailer
    result = cli_runner.invoke(
        mediainfo,
        args=stringify_path(p_video),
        catch_exceptions=False,
    )
    assert result.exit_code == 0
    # some output is present on invocation return
    assert result.output
    # this output is JSON compatible
    json_mediainfo = json.loads(result.output)
    # for our test media file example => the JSON media information is not empty
    assert json_mediainfo
    # simply check on media reference field
    assert json_mediainfo.get("media").get("@ref") == str(p_video)
    # check many media information attributes are defined
    assert len(flatten(json_mediainfo, enumerate_types=(list,))) > 100
