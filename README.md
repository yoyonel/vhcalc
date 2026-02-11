# vhcalc

It's a client-side library that implements a custom algorithm for extracting video hashes (fingerprints) from any video source.

## Installation

```shell
uv sync
```

## Development

This project uses [`just`](https://github.com/casey/just) as a command runner.

### Available commands

*   `just install`: Install project dependencies.
*   `just test`: Run the test suite.
*   `just lint`: Check code quality (Ruff, Mypy).
*   `just format`: Format code (Ruff).
*   `just build`: Build the Python package.
*   `just docker-build`: Build the Docker image.
*   `just run [args]`: Run the application (e.g., `just run --help`).

## Usage

```shell
$ uv run vhcalc --help
Usage: vhcalc [OPTIONS] COMMAND [ARGS]...

Options:
  --version  Show the version and exit.
  --help     Show this message and exit.
imghash*                   Compute image hashes from and to binaries stream
                           (by default: stdin/out)
export-imghash-from-media  extracting and exporting binary video hashes
                           (fingerprints) from any video source
```

### `imghash` default entrypoint

```shell
$ uv run vhcalc imghash --help
Usage: vhcalc imghash [OPTIONS] [INPUT_STREAM] [OUTPUT_STREAM]

  Simple form of the application: Input filepath > image hashes (to stdout by
  default)

Options:
  --image-hashing-method [AverageHashing|PerceptualHashing|PerceptualHashing_Simple|DifferenceHashing|WaveletHashing]
                                  [default: PerceptualHashing]
  --decompress
  --from-url URL
  --help                          Show this message and exit.
```


#### Media into binary images hashes (fingerprints)
```shell
# using pipes for input/output streams
$ cat tests/data/big_buck_bunny_trailer_480p.mkv | \
  # input: binary data from video/media (readable by ffmpeg)
  uv run vhcalc imghash --image-hashing-method PerceptualHashing | \
  # output: binary representation of images hashes (to stdout)
  hexdump | tail -n 8
The frame size for reading (32, 32) is different from the source frame size (854, 480).
*
0001900 93f5 6d91 926a 6585 d2f5 6d91 926a 6585
0001910 92f5 6d91 9a6a 6585 92f5 6c91 9b6e 6485
0001920 92d5 6d91 9a7a 6585 92d5 6591 9a6e e585
0001930 d2d5 6591 9a6a e585 d2d5 2c91 9b6e e485
0001940 d2d5 6d91 926e e581 d2d5 6d91 d26e e181
0001950 d6d5 b581 c26e f181 d5d5 d52a d528 d528
0001960
```
#### Media to hexadecimal representation of images hashes (fingerprints)

```shell
$ cat tests/data/big_buck_bunny_trailer_480p.mkv | \
    # input: binary data from video/media (readable by ffmpeg)
    uv run vhcalc imghash --image-hashing-method PerceptualHashing | \
    # output/input: binary images hashes (through pipe stream)
    uv run vhcalc imghash --decompress | \
    # output: string hexadecimal representation of images hashes (to stdout)
    fold -w 16 | tail -n 8
The frame size for reading (32, 32) is different from the source frame size (854, 480).
d592916d7a9a8565
d59291656e9a85e5
d5d291656a9a85e5
d5d2912c6e9b85e4
d5d2916d6e9281e5
d5d2916d6ed281e1
d5d681b56ec281f1
d5d52ad528d528d5%
```

#### From URL

```shell
  # launching (in background) a webserver deserving `tests/data` files
$ python3 -m http.server -d tests/data & \
  # input: url to tests/data video serving by http server
  uv run vhcalc --from-url http://0.0.0.0:8000/big_buck_bunny_trailer_480p.mkv | \
  # output/input: binary images hashes (through pipe stream)
  uv run vhcalc --decompress | \
  # output: string hexadecimal representation of images hashes (to stdout)
  fold -w 16 | tail -n 8; \
  # killing the http server launch at the beginning
  ps -ef | grep http.server | grep tests/data | grep -v grep | awk '{print $2}' | xargs kill
[1] 2217597
Serving HTTP on 0.0.0.0 port 8000 (http://0.0.0.0:8000/) ...
127.0.0.1 - - [12/Sep/2024 16:36:44] "GET /big_buck_bunny_trailer_480p.mkv HTTP/1.1" 200 -
The frame size for reading (32, 32) is different from the source frame size (854, 480).
d592916d7a9a8565
d59291656e9a85e5
d5d291656a9a85e5
d5d2912c6e9b85e4
d5d2916d6e9281e5
d5d2916d6ed281e1
d5d681b56ec281f1
d5d52ad528d528d5%
[1]  + 2217597 terminated  python3 -m http.server -d tests/data
```

##### From YouTube video

Requirement: [yt-dlp - A feature-rich command-line audio/video downloader](https://github.com/yt-dlp/yt-dlp)

```shell
  # input: Youtube url grab by yt-dlp tool
$ uv run vhcalc --from-url $(yt-dlp --youtube-skip-dash-manifest -g https://www.youtube.com/watch?v=W6QOj6vWmoQ | head -n 1) | \
  # output/input: binary images hashes (through pipe stream)
  uv run vhcalc --decompress | \
  # output: string hexadecimal representation of images hashes (to stdout)
  fold -w 16 | tail -n 8;
The frame size for reading (32, 32) is different from the source frame size (606, 1080).
8adaf123841eb379
8adaf123841eb379
8283bb72f46ce871
8283bb72f46ce871
8283bb72f46ce871
8283bb72f46ce871
8283bb72f46ce871
8283bb72f46ce871%
```

## Docker

Docker hub: [yoyonel/vhcalc](https://hub.docker.com/r/yoyonel/vhcalc/)

```shell
$ docker run -it yoyonel/vhcalc:latest --help
Usage: vhcalc [OPTIONS] COMMAND [ARGS]...

Options:
  --version  Show the version and exit.
  --help     Show this message and exit.
imghash*                   Compute image hashes from and to binaries stream
                           (by default: stdin/out)
export-imghash-from-media  extracting and exporting binary video hashes
                           (fingerprints) from any video source
```

```shell
# with '-i' docker run option, we can use (host) pipes from stdin to stdout (for example)
$ cat tests/data/big_buck_bunny_trailer_480p.mkv | docker run -i --rm yoyonel/vhcalc:latest | md5sum
The frame size for reading (32, 32) is different from the source frame size (854, 480).
bf5c7468df01d78862c847596de92ff3  -

# using HTTP server and url input
$ python3 -m http.server -d tests/data & \
  # input: url to tests/data video serving by http server
  docker run -i --network host yoyonel/vhcalc --from-url http://0.0.0.0:8000/big_buck_bunny_trailer_480p.mkv | \
  # output/input: binary images hashes (through pipe stream)
  docker run -i yoyonel/vhcalc --decompress | \
  # output: string hexadecimal representation of images hashes (to stdout)
  fold -w 16 | tail -n 8; \
  # killing the http server launch at the beginning
  ps -ef | grep http.server | grep tests/data | grep -v grep | awk '{print $2}' | xargs kill
[1] 1929365
Serving HTTP on 0.0.0.0 port 8000 (http://0.0.0.0:8000/) ...
127.0.0.1 - - [13/Sep/2024 14:59:04] "GET /big_buck_bunny_trailer_480p.mkv HTTP/1.1" 200 -
The frame size for reading (32, 32) is different from the source frame size (854, 480).
d592916d7a9a8565
d59291656e9a85e5
d5d291656a9a85e5
d5d2912c6e9b85e4
d5d2916d6e9281e5
d5d2916d6ed281e1
d5d681b56ec281f1
d5d52ad528d528d5%
```

## Contributing
See [Contributing](contributing.md)

## Authors
Lionel Atty <yoyonel@hotmail.com>


Created from [Lee-W/cookiecutter-python-template](https://github.com/Lee-W/cookiecutter-python-template/tree/1.1.2) version 1.1.2
