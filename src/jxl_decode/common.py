"""
Common code used by other modules.
"""


class RawImage:
    """
    Raw image data stored in a List of pixels per channel.

    The pixels are interpreted in row-first.

    This could well be a dictionary, but I like it having defaults.
    """

    def __init__(self):
        self.colourspace = "sRGB"
        self.bitdepth: int = 8  # Bit depth per channel
        self.width: int
        self.height: int
        self.ch0: list[int]
        self.ch1: list[int]
        self.ch2: list[int]

    def __str__(self) -> str:
        pretty_string = "\n".join(
            (
                "RawImage (",
                f"Width: {self.width},",
                f"Height: {self.height},",
                f"Bitdepth: {self.bitdepth},",
                f"Colour Space: {self.colourspace},",
                f"Channel 0: {self.ch0},",
                f"Channel 1: {self.ch1},",
                f"Channel 2: {self.ch2} )",
            )
        )
        return pretty_string


class Bitstream:
    """
    A stream of bits with methods for easy handling.
    """

    def __init__(self, bitstream: bytes) -> None:
        self.bitstream: int = int.from_bytes(bitstream, "little")
        self.shift: int = 0

    def get_bits(self, length: int = 1) -> int:
        bitmask = 2**length - 1
        bits = (self.bitstream >> self.shift) & bitmask
        self.shift += length
        return bits
