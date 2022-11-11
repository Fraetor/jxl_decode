#! /usr/bin/env python3
"""
pyjxl module

This module implements the core code of pyJXL.
"""

from pathlib import Path
from sys import argv


class RawImage:
    """
    Raw image data stored in a NumPy array per channel.

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


def load(file_path: Path) -> bytearray:
    """Loads an image from disk and returns it."""
    with open(file_path, "rb") as f:
        return bytearray(f.read())


def decode(bitstream: bytearray) -> RawImage:
    """Decodes a bitstream using the appropriate decoder."""
    image_type = sniff_image_type(bitstream[:12])
    match image_type:
        case "jxl": return decode_jxl(bitstream)
        case "jpg": return decode_jpg(bitstream)
        case "ppm": return decode_ppm(bitstream)


def save(filename: Path, image_data: RawImage):
    """Saves image to disk as a PNG."""
    raise NotImplementedError


def sniff_image_type(bitstream: bytearray) -> str:
    """
    Determines the image type by sniffing the first few bytes.
    """
    # Test for raw JXL codestream.
    if bitstream[:2] == bytes.fromhex("FF0A"):
        return "jxl"
    # Test for JXL box structure. http://www-internal/2022/18181-2#box-types
    if bitstream[:12] == bytes.fromhex("0000 000C 4A58 4C20 0D0A 870A"):
        return "jxl"
    # Test for PPM.
    if bitstream[:2] == b'P6':
        return "ppm"
    # Test for JPEG/JFIF.
    if bitstream[:2] == bytes.fromhex("FFD8"):
        return "jpg"
    raise ValueError("Not a recognised image type.")


def decode_ppm(bitstream: bytearray) -> RawImage:
    """
    PPM specification: http://davis.lbl.gov/Manuals/NETPBM/doc/ppm.html

    Approx spec: (space is any ASCII whitespace.)
    P6 WIDTH HEIGHT MAXVAL DATA...

    DATA scans top to bottom, left to right. E.g:
    RGB1 RGB2 RGB3
    RGB4 RGB5 RGB6
    RGB7 RGB8 RGB9
    """
    sectioned = bitstream.split(maxsplit=4)

    image = RawImage()
    image.width = int(sectioned[1])
    image.height = int(sectioned[2])
    image.ch0 = []
    image.ch1 = []
    image.ch2 = []

    max_val = int(sectioned[3])
    data = sectioned[4]

    if max_val < 256:
        image.bitdepth = 8
        for y in range(image.height):
            h_strip = []
            for x in range(image.width):
                h_strip.append(data[3*x*y+3*x])
            image.ch0.append(h_strip)

        for y in range(image.height):
            h_strip = []
            for x in range(image.width):
                h_strip.append(data[3*x*y+3*x+1])
            image.ch1.append(h_strip)

        for y in range(image.height):
            h_strip = []
            for x in range(image.width):
                h_strip.append(data[3*x*y+3*x+2])
            image.ch2.append(h_strip)
    else:
        image.bitdepth = 16
        # PPM is big endian, so from_bytes works by default.
        for y in range(image.height):
            h_strip = []
            for x in range(image.width):
                h_strip.append(int.from_bytes(data[6*x*y+6*x:6*x*y+6*x+2]))
            image.ch0.append(h_strip)

        for y in range(image.height):
            h_strip = []
            for x in range(image.width):
                h_strip.append(int.from_bytes(data[6*x*y+6*x+2:6*x*y+6*x+4]))
            image.ch1.append(h_strip)

        for y in range(image.height):
            h_strip = []
            for x in range(image.width):
                h_strip.append(int.from_bytes(data[6*x*y+6*x+4:6*x*y+6*x+6]))
            image.ch2.append(h_strip)

    return image


def decode_jpg(bitstream: bytearray) -> RawImage:
    """
    https://en.wikipedia.org/wiki/JPEG_File_Interchange_Format#File_format_structure
    https://www.w3.org/Graphics/JPEG/jfif3.pdf
    """
    raise NotImplementedError


def decode_jxl(bitstream: bytearray) -> RawImage:
    """
    JXL specification: http://www-internal/2022/18181-1
    """
    raise NotImplementedError


def print_help(exit_code=0):
    """
    Prints out a help message to standard out, then exits.
    """
    print(
        """Usage: pyjxl INPUT_FILE [OUTPUT_FILE]
Decodes the INPUT_FILE, optionally saving to the OUTPUT_FILE.

-h, --help    display this help and exit
pyJXL is intended to decode PPM, JPEG, and JPEG XL files. It outputs to a PNG
file.""")
    exit(exit_code)


if __name__ == "__main__":
    if "-h" in argv or "--help" in argv or not 1 < len(argv) <= 3:
        print_help(0)
    file_in = Path(argv[1])
    if len(argv) == 3:
        file_out = Path(argv[2])
        print(f"Decoding {file_in} and saving to {file_out}...")
        save(file_out, decode(load(file_in)))
    else:
        print(f"Decoding {file_in} and printing output...")
        print(decode(load(file_in)))
