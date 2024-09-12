import subprocess
import threading
import time
from typing import BinaryIO

from imageio_ffmpeg import get_ffmpeg_exe
from imageio_ffmpeg._parsing import LogCatcher, parse_ffmpeg_header
from imageio_ffmpeg._utils import _popen_kwargs, logger


def read_frames_from_binary_stream(
    bin_io_stream: BinaryIO,
    pix_fmt="rgb24",
    bpp=None,
    input_params=None,
    output_params=None,
    bits_per_pixel=None,
    chunk_size_for_input_stream_reading: int = 8_192,
):
    """
    Create a generator to iterate over the frames in a video file.

    It first yields a small metadata dictionary that contains:

    * ffmpeg_version: the ffmpeg version in use (as a string).
    * codec: a hint about the codec used to encode the video, e.g. "h264".
    * source_size: the width and height of the encoded video frames.
    * size: the width and height of the frames that will be produced.
    * fps: the frames per second. Can be zero if it could not be detected.
    * duration: duration in seconds. Can be zero if it could not be detected.

    After that, it yields frames until the end of the video is reached. Each
    frame is a bytes object.

    This function makes no assumptions about the number of frames in
    the data. For one because this is hard to predict exactly, but also
    because it may depend on the provided output_params. If you want
    to know the number of frames in a video file, use count_frames_and_secs().
    It is also possible to estimate the number of frames from the fps and
    duration, but note that even if both numbers are present, the resulting
    value is not always correct.

    Example:

        gen = read_frames(path)
        meta = gen.__next__()
        for frame in gen:
            print(len(frame))

    Parameters:
        bin_io_stream (BinaryIO): .
        pix_fmt (str): the pixel format of the frames to be read.
            The default is "rgb24" (frames are uint8 RGB images).
        input_params (list): Additional ffmpeg input command line parameters.
        output_params (list): Additional ffmpeg output command line parameters.
        bits_per_pixel (int): The number of bits per pixel in the output frames.
            This depends on the given pix_fmt. Default is 24 (RGB)
        bpp (int): DEPRECATED, USE bits_per_pixel INSTEAD. The number of bytes per pixel in the output frames.
            This depends on the given pix_fmt. Some pixel formats like yuv420p have 12 bits per pixel
            and cannot be set in bytes as integer. For this reason the bpp argument is deprecated.
        chunk_size_for_input_stream_reading (int): size (in bits) used for chunk reading from input stream
    """

    # ----- Input args

    # if isinstance(path, pathlib.PurePath):
    #     path = str(path)
    # if not isinstance(path, str):
    #     raise TypeError("Video path must be a string or pathlib.Path.")
    # # Note: Don't check whether it exists. The source could be e.g. a camera.

    pix_fmt = pix_fmt or "rgb24"
    bpp = bpp or 3
    bits_per_pixel = bits_per_pixel or bpp * 8
    input_params = input_params or []
    output_params = output_params or []

    assert isinstance(pix_fmt, str), "pix_fmt must be a string"
    assert isinstance(bits_per_pixel, int), "bpp and bits_per_pixel must be an int"
    assert isinstance(input_params, list), "input_params must be a list"
    assert isinstance(output_params, list), "output_params must be a list"

    # ----- Prepare

    pre_output_params = ["-pix_fmt", pix_fmt, "-vcodec", "rawvideo", "-f", "image2pipe"]

    cmd = [get_ffmpeg_exe()]
    # [Pipe input in to ffmpeg stdin](https://stackoverflow.com/a/45902691)
    # [ffmpeg-protocols.html#pipe](https://ffmpeg.org/ffmpeg-protocols.html#pipe)
    cmd += input_params + ["-i", "pipe:0"]
    cmd += pre_output_params + output_params + ["-"]

    process = subprocess.Popen(
        cmd,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        **_popen_kwargs(prevent_sigint=True),
    )

    # Thread to inject input stream by chunks
    # [How do I write to a Python subprocess' stdin?](https://stackoverflow.com/a/76708895)
    # [Popen.stdin](https://docs.python.org/3/library/subprocess.html#subprocess.Popen.stdin)
    # [Popen's communicate vs stdin.write: Why warning? What instead?](https://www.reddit.com/r/learnpython/comments/17c7h7u/popens_communicate_vs_stdinwrite_why_warning_what/)
    # [cpython/Lib/subprocess.py: def communicate(...)](https://github.com/python/cpython/blob/main/Lib/subprocess.py#L1174)
    # [Send input from one threaded subprocess to another](https://stackoverflow.com/questions/41287291/send-input-from-one-threaded-subprocess-to-another)
    def write_to_input_stream(_process, _bin_io_stream: BinaryIO):
        logger.info(
            f"starting to write to input stream ({chunk_size_for_input_stream_reading=} octets)"
        )
        # [Read file in chunks - RAM-usage, reading strings from binary files](https://stackoverflow.com/a/63563264)
        try:
            while chunk := _bin_io_stream.read(chunk_size_for_input_stream_reading):
                _process.stdin.write(chunk)
                _process.stdin.flush()
        # to prevent error occurred in doctest (at the end)
        except BrokenPipeError:
            pass
        finally:
            _process.stdin.close()
            pass

    thread_write_to_input_stream = threading.Thread(
        target=write_to_input_stream, args=(process, bin_io_stream)
    )
    # Start a thread for injecting binary data to input
    thread_write_to_input_stream.daemon = True
    thread_write_to_input_stream.start()

    log_catcher = LogCatcher(process.stderr)

    # Init policy by which to terminate ffmpeg. May be set to "kill" later.
    stop_policy = "timeout"  # not wait; ffmpeg should be able to quit quickly

    # Enter try block directly after opening the process.
    # We terminate ffmpeg in the final clause.
    # Generators are automatically closed when they get deleted,
    # so the finally block is guaranteed to run.
    try:
        # ----- Load meta data

        # Wait for the log catcher to get the meta information
        etime = time.time() + 10.0
        while log_catcher.is_alive() and not log_catcher.header and time.time() < etime:
            time.sleep(0.01)

        # Check whether we have the information
        if not log_catcher.header:
            err2 = log_catcher.get_text(0.2)
            fmt = "Could not load meta information\n=== stderr ===\n{}"
            raise IOError(fmt.format(err2))
        # TODO: maybe an another log error type for pipe input ... need to look at it !
        # elif "No such file or directory" in log_catcher.header:
        #     raise IOError("{} not found! Wrong path?".format(path))

        meta = parse_ffmpeg_header(log_catcher.header)
        yield meta

        # ----- Read frames

        width, height = meta["size"]
        framesize_bits = width * height * bits_per_pixel
        framesize_bytes = framesize_bits / 8
        assert (
            framesize_bytes.is_integer()
        ), "incorrect bits_per_pixel, framesize in bytes must be an int"
        framesize_bytes = int(framesize_bytes)
        framenr = 0

        while True:
            framenr += 1
            try:
                bb = bytes()
                while len(bb) < framesize_bytes:
                    extra_bytes = process.stdout.read(framesize_bytes - len(bb))
                    if not extra_bytes:
                        if len(bb) == 0:
                            return
                        else:
                            raise RuntimeError(
                                "End of file reached before full frame could be read."
                            )
                    bb += extra_bytes
                yield bb
            except Exception as err:
                err1 = str(err)
                err2 = log_catcher.get_text(0.4)
                fmt = "Could not read frame {}:\n{}\n=== stderr ===\n{}"
                raise RuntimeError(fmt.format(framenr, err1, err2))

    except GeneratorExit:
        # Note that GeneratorExit does not inherit from Exception but BaseException
        pass

    except Exception:
        # Normal exceptions fall through
        raise

    except BaseException:
        # Detect KeyboardInterrupt / SystemExit: don't wait for ffmpeg to quit
        stop_policy = "kill"
        raise

    finally:
        # waiting the end of the (Producer) thread
        try:
            thread_write_to_input_stream.join(timeout=1)
        except TimeoutError:
            logger.warning(
                "Consumer (FFMPEG stdout) stop before Producer (FFMPEG stdin)."
            )

        # Stop the LogCatcher thread, which reads from stderr.
        log_catcher.stop_me()

        # Make sure that ffmpeg is terminated.
        if process.poll() is None:
            # Ask ffmpeg to quit
            try:
                # I read somewhere that modern ffmpeg on Linux prefers a
                # "ctrl-c", but tests so far suggests sending q is more robust.
                # > p.send_signal(signal.SIGINT)
                # Sending q via communicate works, but can hang (see #17)
                # > p.communicate(b"q")
                # So let's do similar to what communicate does, but without
                # reading stdout (which may block). It looks like only closing
                # stdout is enough (tried Windows+Linux), but let's play safe.
                # Found that writing to stdin can cause "Invalid argument" on
                # Windows # and "Broken Pipe" on Unix.
                # p.stdin.write(b"q")  # commented out in v0.4.1
                process.stdout.close()
                # process.stdin.close() -> not here, the thread writing into input stream closes it
                # p.stderr.close() -> not here, the log_catcher closes it
            except Exception as err:  # pragma: no cover
                logger.warning("Error while attempting stop ffmpeg (r): " + str(err))

            if stop_policy == "timeout":
                # Wait until timeout, produce a warning and kill if it still exists
                try:
                    etime = time.time() + 1.5
                    while time.time() < etime and process.poll() is None:
                        time.sleep(0.01)
                finally:
                    if process.poll() is None:  # pragma: no cover
                        logger.warning("We had to kill ffmpeg to stop it.")
                        process.kill()

            else:  # stop_policy == "kill"
                # Just kill it
                process.kill()


# TODO: need to mutualise code (too much duplications)
def read_frames_from_url(
    url,
    pix_fmt="rgb24",
    bpp=None,
    input_params=None,
    output_params=None,
    bits_per_pixel=None,
):
    """
    Create a generator to iterate over the frames in a video file.

    It first yields a small metadata dictionary that contains:

    * ffmpeg_version: the ffmpeg version in use (as a string).
    * codec: a hint about the codec used to encode the video, e.g. "h264".
    * source_size: the width and height of the encoded video frames.
    * size: the width and height of the frames that will be produced.
    * fps: the frames per second. Can be zero if it could not be detected.
    * duration: duration in seconds. Can be zero if it could not be detected.

    After that, it yields frames until the end of the video is reached. Each
    frame is a bytes object.

    This function makes no assumptions about the number of frames in
    the data. For one because this is hard to predict exactly, but also
    because it may depend on the provided output_params. If you want
    to know the number of frames in a video file, use count_frames_and_secs().
    It is also possible to estimate the number of frames from the fps and
    duration, but note that even if both numbers are present, the resulting
    value is not always correct.

    Example:

        gen = read_frames(path)
        meta = gen.__next__()
        for frame in gen:
            print(len(frame))

    Parameters:
        url (str): url pointing to streaming video (for example from YouTube).
        pix_fmt (str): the pixel format of the frames to be read.
            The default is "rgb24" (frames are uint8 RGB images).
        input_params (list): Additional ffmpeg input command line parameters.
        output_params (list): Additional ffmpeg output command line parameters.
        bits_per_pixel (int): The number of bits per pixel in the output frames.
            This depends on the given pix_fmt. Default is 24 (RGB)
        bpp (int): DEPRECATED, USE bits_per_pixel INSTEAD. The number of bytes per pixel in the output frames.
            This depends on the given pix_fmt. Some pixel formats like yuv420p have 12 bits per pixel
            and cannot be set in bytes as integer. For this reason the bpp argument is deprecated.
    """

    # ----- Input args
    pix_fmt = pix_fmt or "rgb24"
    bpp = bpp or 3
    bits_per_pixel = bits_per_pixel or bpp * 8
    input_params = input_params or []
    output_params = output_params or []

    assert isinstance(pix_fmt, str), "pix_fmt must be a string"
    assert isinstance(bits_per_pixel, int), "bpp and bits_per_pixel must be an int"
    assert isinstance(input_params, list), "input_params must be a list"
    assert isinstance(output_params, list), "output_params must be a list"

    # ----- Prepare

    pre_output_params = ["-pix_fmt", pix_fmt, "-vcodec", "rawvideo", "-f", "image2pipe"]

    cmd = [get_ffmpeg_exe()]
    cmd += input_params + ["-i", url]
    cmd += pre_output_params + output_params + ["-"]

    process = subprocess.Popen(
        cmd,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        **_popen_kwargs(prevent_sigint=True),
    )

    log_catcher = LogCatcher(process.stderr)

    # Init policy by which to terminate ffmpeg. May be set to "kill" later.
    stop_policy = "timeout"  # not wait; ffmpeg should be able to quit quickly

    # Enter try block directly after opening the process.
    # We terminate ffmpeg in the final clause.
    # Generators are automatically closed when they get deleted,
    # so the finally block is guaranteed to run.
    try:
        # ----- Load meta data

        # Wait for the log catcher to get the meta information
        etime = time.time() + 10.0
        while log_catcher.is_alive() and not log_catcher.header and time.time() < etime:
            time.sleep(0.01)

        # Check whether we have the information
        if not log_catcher.header:
            err2 = log_catcher.get_text(0.2)
            fmt = "Could not load meta information\n=== stderr ===\n{}"
            raise IOError(fmt.format(err2))
        # elif "No such file or directory" in log_catcher.header:
        #     raise IOError("{} not found! Wrong path?".format(path))

        meta = parse_ffmpeg_header(log_catcher.header)
        yield meta

        # ----- Read frames

        width, height = meta["size"]
        framesize_bits = width * height * bits_per_pixel
        framesize_bytes = framesize_bits / 8
        assert (
            framesize_bytes.is_integer()
        ), "incorrect bits_per_pixel, framesize in bytes must be an int"
        framesize_bytes = int(framesize_bytes)
        framenr = 0

        while True:
            framenr += 1
            try:
                bb = bytes()
                while len(bb) < framesize_bytes:
                    extra_bytes = process.stdout.read(framesize_bytes - len(bb))
                    if not extra_bytes:
                        if len(bb) == 0:
                            return
                        else:
                            raise RuntimeError(
                                "End of file reached before full frame could be read."
                            )
                    bb += extra_bytes
                yield bb
            except Exception as err:
                err1 = str(err)
                err2 = log_catcher.get_text(0.4)
                fmt = "Could not read frame {}:\n{}\n=== stderr ===\n{}"
                raise RuntimeError(fmt.format(framenr, err1, err2))

    except GeneratorExit:
        # Note that GeneratorExit does not inherit from Exception but BaseException
        pass

    except Exception:
        # Normal exceptions fall through
        raise

    except BaseException:
        # Detect KeyboardInterrupt / SystemExit: don't wait for ffmpeg to quit
        stop_policy = "kill"
        raise

    finally:
        # Stop the LogCatcher thread, which reads from stderr.
        log_catcher.stop_me()

        # Make sure that ffmpeg is terminated.
        if process.poll() is None:
            # Ask ffmpeg to quit
            try:
                # I read somewhere that modern ffmpeg on Linux prefers a
                # "ctrl-c", but tests so far suggests sending q is more robust.
                # > p.send_signal(signal.SIGINT)
                # Sending q via communicate works, but can hang (see #17)
                # > p.communicate(b"q")
                # So let's do similar to what communicate does, but without
                # reading stdout (which may block). It looks like only closing
                # stdout is enough (tried Windows+Linux), but let's play safe.
                # Found that writing to stdin can cause "Invalid argument" on
                # Windows # and "Broken Pipe" on Unix.
                # p.stdin.write(b"q")  # commented out in v0.4.1
                process.stdout.close()
                process.stdin.close()
                # p.stderr.close() -> not here, the log_catcher closes it
            except Exception as err:  # pragma: no cover
                logger.warning("Error while attempting stop ffmpeg (r): " + str(err))

            if stop_policy == "timeout":
                # Wait until timeout, produce a warning and kill if it still exists
                try:
                    etime = time.time() + 1.5
                    while time.time() < etime and process.poll() is None:
                        time.sleep(0.01)
                finally:
                    if process.poll() is None:  # pragma: no cover
                        logger.warning("We had to kill ffmpeg to stop it.")
                        process.kill()

            else:  # stop_policy == "kill"
                # Just kill it
                process.kill()
