from pathlib import Path

# https://pypi.org/project/click-pathlib/
from tempfile import gettempdir
from typing import Optional

from rich import get_console
from rich.console import Console

from vhcalc.tools.chunk import chunks
from vhcalc.tools.imghash import imghash_to_bytes, rawframe_to_imghash
from vhcalc.tools.progress_bar import configure_progress_bar

from .reader_frames import build_reader_frames


def export_imghash_from_media(
    input_media: Path,
    output_file: Optional[Path] = None,
    chunk_nb_seconds: int = 15,
    console: Optional[Console] = None,
) -> Path:
    console = console or get_console()
    # Read a video file
    it_reader_frame, media_metadata = build_reader_frames(input_media)
    console.print(media_metadata)
    nb_frames_to_read = media_metadata.nb_frames
    chunk_size = int(media_metadata.fps * chunk_nb_seconds)
    #
    console.print(f"Number of frames to read: {nb_frames_to_read}")
    console.print(f"Chunk size (nb frames): {chunk_size}")

    # manage export
    output_file = (
        Path(output_file)
        if output_file
        # https://bandit.readthedocs.io/en/latest/plugins/b108_hardcoded_tmp_directory.html
        else Path(gettempdir()) / f"{input_media.name}.{media_metadata.fps}fps.phash"
    )
    output_file.unlink(missing_ok=True)
    console.print(f"output_file: {str(output_file)}")

    # configure progress bar
    progress_bar, pb_task_id = configure_progress_bar(
        input_media.name, nb_frames_to_read * 8, console
    )
    pb_advance = chunk_size * 8

    # processing (export)
    with progress_bar:
        gen_imghashes = map(rawframe_to_imghash, it_reader_frame)
        gen_chunk_imghashes = chunks(gen_imghashes, chunk_size)
        for chunk_imghashes in gen_chunk_imghashes:
            with output_file.open("ab") as fo:
                for frame_hash_binary in map(imghash_to_bytes, chunk_imghashes):
                    fo.write(frame_hash_binary)
            progress_bar.update(pb_task_id, advance=pb_advance, refresh=True)
    return output_file
