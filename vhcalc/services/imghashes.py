from functools import partial
from io import BufferedReader
from pathlib import Path

# https://pypi.org/project/click-pathlib/
from tempfile import gettempdir
from typing import Iterable, Optional

from rich import get_console

from vhcalc.models.imghash_function import ImageHashingFunction
from vhcalc.services.reader_frames import build_reader_frames
from vhcalc.tools.chunk import chunks
from vhcalc.tools.imghash import imghash_to_bytes, rawframe_to_imghash
from vhcalc.tools.progress_bar import configure_progress_bar

console = get_console()


def compute_imghash_from_media_from_binary_stream(
    binary_stream: BufferedReader,
    chunk_nb_seconds: int = 15,
    fn_imagehash: ImageHashingFunction = ImageHashingFunction.PerceptualHashing,
) -> Iterable[bytes]:
    """
    Compute images hashes from media input stream (readable with ffmpeg)

    Args:
        binary_stream (BufferedReader): binary stream to read from media input
        chunk_nb_seconds (int): Chunk size in seconds used for generating images hashes from media decompression.
        fn_imagehash (ImageHashingFunction): ImageHash function for transforming PIL.Image to ImageHash

    Yields:
        Iterable[bytes]: The next binary image hash from media input stream

    Example:
        >>> media_path = Path("tests/data/big_buck_bunny_trailer_480p.mkv")
        >>> next(compute_imghash_from_media_from_binary_stream(media_path.open("rb")))
        b'\xd5\xd5*\xd5*\xd4*\xd4'
    """
    # Read a video file
    it_reader_frame, media_metadata = build_reader_frames(binary_stream)
    chunk_size = int(media_metadata.fps * chunk_nb_seconds)

    # configure chunk
    gen_imghashes = map(
        partial(rawframe_to_imghash, fn_imagehash=fn_imagehash), it_reader_frame
    )
    gen_chunk_imghashes = chunks(gen_imghashes, chunk_size)
    # for each chunk of frames
    for chunk_imghashes in gen_chunk_imghashes:
        for frame_hash_binary in map(imghash_to_bytes, chunk_imghashes):
            # and write (chunk of) images hashes result on export file
            yield frame_hash_binary


def export_imghash_from_media(
    input_media: Path,
    output_file: Optional[Path] = None,
    chunk_nb_seconds: int = 15,
    unlink_export_file: bool = True,
) -> Path:
    """
    Export images hashes from media (readable with ffmpeg)

    Args:
        input_media (Path): Path object targeting the input media.
        output_file (Optional[Path]): Path object for the output file. If not given, a temporary file is created.
        chunk_nb_seconds (int): Chunk size in seconds used for generating images hashes from media decompression.
        unlink_export_file (bool): Option for apply Path.unlink() on output file.

    Returns:
        pathlib.Path: Path for the output file that contain binary images hashes.

    """
    # Read a video file
    it_reader_frame, media_metadata = build_reader_frames(input_media)
    nb_frames_to_read = media_metadata.nb_frames
    chunk_size = int(media_metadata.fps * chunk_nb_seconds)

    console.print(f"{media_metadata}")
    console.print(f"Number of frames to read: {nb_frames_to_read}")
    console.print(f"Chunk size (nb frames): {chunk_size}")

    # manage export
    if not output_file:
        # https://bandit.readthedocs.io/en/latest/plugins/b108_hardcoded_tmp_directory.html
        output_file = (
            Path(gettempdir()) / f"{input_media.name}.{media_metadata.fps}fps.phash"
        )

    # remove/unlink export file if exist
    if unlink_export_file:
        output_file.unlink(missing_ok=True)

    console.print(f"output_file: {str(output_file)}")

    # configure progress bar
    progress_bar, pb_task_id = configure_progress_bar(
        input_media.name, nb_frames_to_read * 8, console
    )
    pb_advance = chunk_size * 8

    with progress_bar:
        gen_imghashes = map(rawframe_to_imghash, it_reader_frame)
        gen_chunk_imghashes = chunks(gen_imghashes, chunk_size)
        # for each chunk of frames
        for chunk_imghashes in gen_chunk_imghashes:
            # ... open/write and close export file in binary append mode
            with output_file.open("ab") as fo:
                # consume generator: chunk frame to image hash
                for frame_hash_binary in map(imghash_to_bytes, chunk_imghashes):
                    # and write (chunk of) images hashes result on export file
                    fo.write(frame_hash_binary)
            # update progress bar synchronize with chunk progression
            progress_bar.update(pb_task_id, advance=pb_advance, refresh=True)
    return output_file
