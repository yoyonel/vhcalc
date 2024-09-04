[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg?style=flat-square)](http://makeapullrequest.com)
[![Conventional Commits](https://img.shields.io/badge/Conventional%20Commits-1.0.0-yellow.svg?style=flat-square)](https://conventionalcommits.org)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Github Actions](https://github.com/yoyonel/vhcalc/actions/workflows/python-check.yaml/badge.svg)](https://github.com/yoyonel/vhcalc/wayback-machine-saver/actions/workflows/python-check.yaml)

[![PyPI Package latest release](https://img.shields.io/pypi/v/vhcalc.svg?style=flat-square)](https://pypi.org/project/vhcalc/)
[![PyPI Package download count (per month)](https://img.shields.io/pypi/dm/vhcalc?style=flat-square)](https://pypi.org/project/vhcalc/)
[![Supported versions](https://img.shields.io/pypi/pyversions/vhcalc.svg?style=flat-square)](https://pypi.org/project/vhcalc/)

[![Docker Image Size (latest semver)](https://img.shields.io/docker/image-size/yoyonel/vhcalc?sort=semver)](https://hub.docker.com/r/yoyonel/vhcalc/)

[![Coverage Status](https://coveralls.io/repos/github/yoyonel/vhcalc/badge.svg?branch=main)](https://coveralls.io/github/yoyonel/vhcalc?branch=main)

# vhcalc

It's a client-side library that implements a custom algorithm for extracting video hashes (fingerprints) from any video source.

## Getting Started

### Prerequisites
* [Python](https://www.python.org/downloads/)

## Usage

```sh
$ vhcalc --help
Usage: vhcalc [OPTIONS] COMMAND [ARGS]...

Options:
  --version  Show the version and exit.
  --help     Show this message and exit.
imghash*                   Compute image hashes from and to binaries stream
                           (by default: stdin/out)
export-imghash-from-media  extracting and exporting binary video hashes
                           (fingerprints) from any video source
```


## Docker

Docker hub: [yoyonel/vhcalc](https://hub.docker.com/r/yoyonel/vhcalc/)

```sh
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
$ cat tests/data/big_buck_bunny_trailer_480p.mkv | docker run -i --rm yoyonel/vhcalc:latest | md5sum
The frame size for reading (32, 32) is different from the source frame size (854, 480).
bf5c7468df01d78862c847596de92ff3  -
```

## Contributing
See [Contributing](contributing.md)

## Authors
Lionel Atty <yoyonel@hotmail.com>


Created from [Lee-W/cookiecutter-python-template](https://github.com/Lee-W/cookiecutter-python-template/tree/1.1.2) version 1.1.2
