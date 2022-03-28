[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg?style=flat-square)](http://makeapullrequest.com)
[![Conventional Commits](https://img.shields.io/badge/Conventional%20Commits-1.0.0-yellow.svg?style=flat-square)](https://conventionalcommits.org)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Github Actions](https://github.com/yoyonel/vhcalc/actions/workflows/python-check.yaml/badge.svg)](https://github.com/yoyonel/vhcalc/wayback-machine-saver/actions/workflows/python-check.yaml)

[![PyPI Package latest release](https://img.shields.io/pypi/v/vhcalc.svg?style=flat-square)](https://pypi.org/project/vhcalc/)
[![PyPI Package download count (per month)](https://img.shields.io/pypi/dm/vhcalc?style=flat-square)](https://pypi.org/project/vhcalc/)
[![Supported versions](https://img.shields.io/pypi/pyversions/vhcalc.svg?style=flat-square)](https://pypi.org/project/vhcalc/)


# vhcalc

It's a client-side library that implements a custom algorithm for extracting video hashes (fingerprints) from any video source.

## Getting Started

### Prerequisites
* [Python](https://www.python.org/downloads/)

## Usage

```shell
╰─ export_imghash_from_media --help  
Usage: export_imghash_from_media [OPTIONS]

  This script exporting binary images hashes (fingerprints) from (any) media
  (video file)

Options:
  --version                       Show the version and exit.
  -r, --medias_pattern PATH-OR-GLOB
                                  Pattern to find medias  [required]
  -o, --output-file PATH          File where to write images hashes.
  --help                          Show this message and exit.
```

## Contributing
See [Contributing](contributing.md)

## Authors
Lionel Atty <yoyonel@hotmail.com>


Created from [Lee-W/cookiecutter-python-template](https://github.com/Lee-W/cookiecutter-python-template/tree/1.1.2) version 1.1.2
