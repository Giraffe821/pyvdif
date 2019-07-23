import struct
import pathlib

file_path = pathlib.Path("./sample.vdif").expanduser()
VDIF_HEADER_BYTE_SIZE = 32
with file_path.open("rb") as f:
    header_bytes = f.read(VDIF_HEADER_BYTE_SIZE)
    words = struct.unpack("<8I", header_bytes)

# coding: utf-8
from typing import Callable, Sequence

Words = Sequence[int]
Parser = Callable[[Words], int]


def make_parser(word_index: int, bit_index: int, bit_length: int) -> Parser:
    """Construct a function that converts specific bits from a header.

    The function acts on a tuple/array of 32-bits words, extracting given bits
    from a specific word and convert then to a integer.
    The parameters are those that define header keywords, and the parser do
    ``(words[word_index] >> bit_index) & ((1 << bit_length) - 1)``.

    Args:
        word_index (int): Index into the tuple of words passed to the function.
        bit_index (int): Index to the starting bit of the part to be extracted.
        bit_length (int): Number of bits to be extracted.

    Return:
        parser (function): A converter of specific bits from a header.

    Raises:
        ValueError: It the size of specific bits is less than or equal to 0
            or greater than 32.
    """
    if not 0 < bit_index + bit_length <= 32:
        raise ValueError(
            "the size of specific bits expected to be greater than 0 and less than 32, "
            f"got {bit_index + bit_length}"
        )

    def parser(words: Words) -> int:
        bit_mask = (1 << bit_length) - 1
        return (words[word_index] >> bit_index) & bit_mask

    return parser()


class Header_common:
    bit_specs = {
        "seconds": (0, 0, 30),
        "legacy": (0, 30, 1),
        "invalid": (0, 31, 1),
        "data_frame": (1, 0, 24),
        "ref_epoch": (1, 24, 6),
        "unassigned": (1, 30, 2),
        "data_frame_length": (2, 0, 24),
        "log_2_channels": (2, 24, 5),
        "vdif_version": (2, 29, 3),
        "station": (3, 0, 16),
        "thread": (3, 16, 10),
        "bit_sample": (3, 26, 5),
        "data_type": (3, 31, 1),
    }

    def __init__(self):
        for key, val in self.bit_specs.items():
            self.__setattr__(key, self.make_parser(*val))
            # setattr(self, key, self.make_parser(*val))

    def make_parser(self, word_index: int, bit_index: int, bit_length: int) -> Parser:
        def parser(words: Words) -> int:
            bit_mask = (1 << bit_length) - 1
            return (words[word_index] >> bit_index) & bit_mask

        return parser(words)


hc = Header_common()


class Header_vdif3(Header_common):
    def __init__(self):
        super().__init__()
        for key, val in self.vdif3.items():
            self.__setattr__(key, self.make_parser(*val))

    vdif3 = {
        "sampling_rate": (4, 0, 23),
        "unit": (4, 23, 1),
        "edv": (4, 24, 8),
        "sync pattern": (5, 0, 32),
        "loif_freq": (6, 0, 32),
        "personality type": (7, 0, 8),
        "minor_rev": (7, 8, 4),
        "major_rev": (7, 12, 4),
        "esb": (7, 16, 1),
        "sub band": (7, 17, 3),
        "_if": (7, 20, 4),
        "dbe_unit": (7, 24, 4),
        "ua": (7, 28, 4),
    }


h3 = Header_vdif3()
