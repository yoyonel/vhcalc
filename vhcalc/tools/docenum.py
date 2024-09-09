"""
# [How can I attach documentation to members of a python enum?](https://stackoverflow.com/questions/50473951/how-can-i-attach-documentation-to-members-of-a-python-enum/50473952#50473952)
"""

from enum import Enum


class DocEnum(Enum):
    def __new__(cls, value, doc=None):  # type: ignore
        self = object.__new__(cls)
        self._value_ = value
        if doc is not None:
            self.__doc__ = doc
        return self

    def __call__(self, *args, **kwargs):  # type: ignore
        return self.value(*args, **kwargs)
