"""
Common code used by other modules.
"""


class RawImage:
    """
    Raw image data stored in a List of Lists per channel.

    This could well be a dictionary, but I like it having defaults.
    """

    def __init__(self):
        self.colourspace = "sRGB"
        self.bitdepth: int = 8  # Bit depth per channel
        self.width: int
        self.height: int
        self.ch0: list[list]
        self.ch1: list[list]
        self.ch2: list[list]

    def __str__(self) -> str:
        pretty_string = "RawImage (\n" + \
            f"Width: {self.width},\n" + \
            f"Height: {self.height},\n" + \
            f"Bitdepth: {self.bitdepth},\n" + \
            f"Colour Space: {self.colourspace},\n" + \
            f"Channel 0: {self.ch0},\n" + \
            f"Channel 1: {self.ch1},\n" + \
            f"Channel 2: {self.ch2} )"
        return pretty_string
