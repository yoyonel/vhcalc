from importlib.metadata import version
from pathlib import Path

from vhcalc.app import export_imghash_from_media
from vhcalc.services.reader_frames import build_reader_frames


def test_cli_export_imghash(big_buck_bunny_trailer, cli_runner, tmpdir):
    p_video = big_buck_bunny_trailer
    resource_video_name = p_video.stem
    binary_img_hash_file = tmpdir.mkdir("phash") / f"{resource_video_name}.phash"
    result = cli_runner.invoke(
        export_imghash_from_media,
        args=f"-r {str(p_video)} -o {binary_img_hash_file}",
        catch_exceptions=False,
    )
    _, meta = build_reader_frames(big_buck_bunny_trailer)
    assert result.exit_code == 0
    expected_size_binary_file = meta.nb_frames * 8
    assert Path(binary_img_hash_file).stat().st_size == expected_size_binary_file


def test_cli_version(cli_runner):
    result = cli_runner.invoke(
        export_imghash_from_media,
        args="--version",
        catch_exceptions=False,
    )
    assert result.exit_code == 0
    app_name_expected = "export-imghash-from-media"
    version_expected = version("vhcalc")
    assert result.output == f"{app_name_expected}, version {version_expected}\n"
