"""
https://stackoverflow.com/questions/8290397/how-to-split-an-iterable-in-constant-size-chunks
"""

from itertools import chain, islice
from typing import Any, Iterator


def chunks(iterable: Iterator[Any], size: int) -> Iterator[Any]:
    """
    >>> list(chunks(range(10), 3))
    [[0, 1, 2], [3, 4, 5], [6, 7, 8], [9]]
    """
    iterator = iter(iterable)
    for first in iterator:
        yield list(chain([first], islice(iterator, size - 1)))
