"""
"""


class URL(str):
    def __init__(self, url: str):
        if not (
            url.startswith("https://")
            or url.startswith("http://")
            or url.startswith("ftp://")
        ):
            raise AssertionError(url)
