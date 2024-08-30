# from: https://gitlab.com/abraxos/click-path/-/blob/a1536f8a2dcbcee026e77a23cc515fe0decb824d/click_path/core.py
from glob import iglob
from os import R_OK, W_OK, access
from pathlib import Path
from typing import Iterable, Tuple

import rich_click as click
from typeguard import typechecked


class GlobPaths(click.ParamType):
    """
    This class is designed to allow users of a click application to pass in a
    glob-based file pattern with filtering and other various requirements.
    While some of the parameters are very similar to those found in the
    click.Path type, they are more geared towards filtering out files that do
    not fit the given requirements and non-existent files are not really
    meaningful for globbing.
    """

    name = "Path-or-Glob"

    @typechecked
    def __init__(
        self,
        files_okay: bool = True,
        dirs_okay: bool = True,
        writable_only: bool = False,
        readable_only: bool = True,
        resolve: bool = False,
        at_least_one: bool = True,
    ):
        self.files_okay = files_okay
        self.dirs_okay = dirs_okay
        self.writable_only = writable_only
        self.readable_only = readable_only
        self.resolve = resolve
        self.at_least_one = at_least_one

    @typechecked
    def _validated_path(self, file_path: Path) -> Tuple[Path, bool, str]:
        if not file_path.exists():
            return file_path, False, "does not exist"
        if self.writable_only and not access(str(file_path), W_OK):
            return file_path, False, "exists, but is not writable"
        if self.readable_only and not access(str(file_path), R_OK):
            return file_path, False, "exists, but is not readable"
        if not self.files_okay and file_path.is_file():
            return file_path, False, "exists, is a file"
        if not self.dirs_okay and file_path.is_dir():
            return file_path, False, "exists, is a directory"
        return file_path, True, "valid"

    @typechecked
    def convert(
        self, value: str, param: click.Parameter, ctx: click.Context
    ) -> Iterable[Path]:
        validation_results = [self._validated_path(Path(p)) for p in iglob(value)]
        if self.at_least_one and not any(valid for _, valid, __ in validation_results):
            summary = "\n".join(
                f"\t{path}: {why}" for path, _, why in validation_results
            )
            self.fail(
                f'No paths from "{value}" matched the requirements: [{", ".join(self.filters())}]\n{summary}',
                param,
                ctx,
            )
        return [
            path if not self.resolve else path.resolve()
            for path, _, __ in validation_results
        ]

    @typechecked
    def filters(self) -> Iterable[str]:
        filters = []
        if self.files_okay:
            filters.append("files")
        if self.dirs_okay:
            filters.append("directories")
        if self.writable_only:
            filters.append("write-permissions")
        if self.readable_only:
            filters.append("read-permissions")
        return filters
