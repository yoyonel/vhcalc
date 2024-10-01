from functools import partial
from io import BufferedReader, BytesIO
from pathlib import Path

# https://pypi.org/project/click-pathlib/
from tempfile import gettempdir
from typing import Iterable, Optional, Union

from imagehash import ImageHash
from rich import get_console

from vhcalc.models import URL, ImageHashingFunction
from vhcalc.services.reader_frames import build_reader_frames
from vhcalc.tools.chunk import chunks
from vhcalc.tools.imghash import bytes_to_imghash, imghash_to_bytes, rawframe_to_imghash
from vhcalc.tools.progress_bar import configure_progress_bar

console = get_console()


def b2b_stream_to_imghash(
    # FIXME: ugly need to refactor
    binary_stream: Union[BufferedReader, URL],
    chunk_size_in_frames: int = 15 * 25,
    fn_imagehash: ImageHashingFunction = ImageHashingFunction.PerceptualHashing,
) -> Iterable[bytes]:
    """
    Compute images hashes from file (media/video) binary content stream (send to ffmpeg)

    Args:
        binary_stream (BufferedReader): binary stream read from media file input
        chunk_size_in_frames (int): Chunk size in frames used for generating images hashes from media decompression.
        fn_imagehash (ImageHashingFunction): ImageHash function for transforming PIL.Image to ImageHash

    Yields:
        Iterable[bytes]: The next binary image hash from media input stream

    Example:
        >>> media_path = Path("tests/data/big_buck_bunny_trailer_480p.mkv")
        >>> next(b2b_stream_to_imghash(media_path.open("rb")))
        b'\xd5\xd5*\xd5*\xd4*\xd4'
    """
    # Read a video file
    it_reader_frame, _ = build_reader_frames(binary_stream)
    chunk_size = chunk_size_in_frames

    # configure chunk
    gen_imghashes = map(
        partial(rawframe_to_imghash, fn_imagehash=fn_imagehash), it_reader_frame
    )
    gen_chunk_imghashes = chunks(gen_imghashes, chunk_size)
    # for each chunk of frames
    for chunk_imghashes in gen_chunk_imghashes:
        for bin_imghash in map(imghash_to_bytes, chunk_imghashes):
            # and write (chunk of) images hashes result on export file
            yield bin_imghash


def a2b_imghash(
    binary_stream: BufferedReader,
    chunk_size: int = 8 * 1024,
) -> Iterable[ImageHash]:
    """

    Args:
        binary_stream (BufferedReader): expected binary stream to read compatible with images hashes binary format.
        chunk_size: size (in bits) used for chunk reading from input stream

    Returns:

    Examples:
        >>> bin_imghashes = b'\\xd5\\xd5*\\xd5*\\xd4*\\xd4' * 8
        >>> bin_stream = BytesIO(bin_imghashes)
        >>> imghash_reconstructed = next(a2b_imghash(bin_stream))
        >>> str(imghash_reconstructed)
        'd5d52ad52ad42ad4'
    """
    while chunk_bin_imghash := binary_stream.read(chunk_size):
        stream_bin_imghash = BytesIO(chunk_bin_imghash)
        while bin_imghash := stream_bin_imghash.read(8):
            yield bytes_to_imghash(bin_imghash)


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
