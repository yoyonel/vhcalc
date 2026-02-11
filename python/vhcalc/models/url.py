class URL(str):
    def __new__(cls, url: str) -> "URL":
        if not (
            url.startswith("https://")
            or url.startswith("http://")
            or url.startswith("ftp://")
        ):
            raise ValueError(f"Invalid URL: {url}")
        return super().__new__(cls, url)
