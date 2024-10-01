import imagehash

from vhcalc.tools.docenum import DocEnum


class ImageHashingFunction(DocEnum):
    """
    >>> assert all(name_fn_img_hash in ImageHashingFunction.__doc__ for name_fn_img_hash in {"Average Hash computation",
    ... "Perceptual Hash computation.", "Difference Hash computation. computes differences horizontally",
    ... "Wavelet Hash computation."})
    >>>
    >>> from pathlib import Path
    >>> from vhcalc.services.imghashes import b2b_stream_to_imghash
    >>>
    >>> media_path = Path("tests/data/big_buck_bunny_trailer_480p.mkv")
    >>> it_imghash = b2b_stream_to_imghash(media_path.open("rb"),
    ... fn_imagehash=ImageHashingFunction.AverageHashing)
    >>> print(next(it_imghash))
    b'\xfe\xfe\xfe\xfe\xfe\xfe\xfe\xfe'
    """

    AverageHashing = imagehash.average_hash, "Average Hash computation"
    PerceptualHashing = imagehash.phash, "Perceptual Hash computation."
    PerceptualHashing_Simple = imagehash.phash_simple, "Perceptual Hash computation."
    DifferenceHashing = (
        imagehash.dhash,
        "Difference Hash computation. computes differences horizontally",
    )
    WaveletHashing = imagehash.whash, "Wavelet Hash computation."

    # TODO: return multiple images hash, not handle yet.
    # CropResistantHashing = imagehash.crop_resistant_hash

    # [How to get all values from python enum class?](https://stackoverflow.com/questions/29503339/how-to-get-all-values-from-python-enum-class)
    @classmethod
    def names(cls) -> list[str]:
        return list(map(lambda c: c.name, cls))
