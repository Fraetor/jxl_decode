#! /usr/bin/env python3
"""
pyjxl module

This module implements the core code of pyJXL.
"""

from pathlib import Path
from sys import argv

import numpy as np


class RawImage:
    """
    Raw image data stored in a NumPy array per channel.
    """

    def __init__(self):
        self.width: int = 0
        self.height: int = 0
        self.colourspace = "sRGB"
        self.ch0 = np.array([[]])
        self.ch1 = np.array([[]])
        self.ch2 = np.array([[]])


def sniff_image_type(bitstream: bytearray) -> str:
    """
    Determines the image type by sniffing the first few bytes.
    """
    # Test for raw JXL codestream.
    if bitstream[:2] == 0xFF0A:
        return "jxl"
    # Test for JXL box structure. http://www-internal/2022/18181-2#box-types
    if bitstream[:12] == 0x0000_000C_4A58_4C20_0D0A_870A:
        return "jxl"
    # Test for PPM.
    if bitstream[:2] == b'P6':
        return "ppm"
    # Test for JPEG/JFIF.
    if bitstream[:2] == 0xFFD8:
        return "jpg"
    raise ValueError("Not a recognised image type.")


def decode_ppm(bitstream: bytearray) -> RawImage:
    # PPM specification: http://davis.lbl.gov/Manuals/NETPBM/doc/ppm.html
    raise NotImplementedError


def decode_jpg(bitstream: bytearray) -> RawImage:
    # https://en.wikipedia.org/wiki/JPEG_File_Interchange_Format#File_format_structure
    # https://www.w3.org/Graphics/JPEG/jfif3.pdf
    raise NotImplementedError


def decode_jxl(bitstream: bytearray) -> RawImage:
    # JXL specification: http://www-internal/2022/18181-1
    raise NotImplementedError


def decode(bitstream: bytearray) -> RawImage:
    """Decodes a bitstream using the appropriate decoder\."""
    image_type = sniff_image_type(bitstream[:12])
    match image_type:
        case "jxl": return decode_jxl(bitstream)
        case "jpg": return decode_jpg(bitstream)
        case "ppm": return decode_ppm(bitstream)


def save(filename: Path, image_data: RawImage):
    """
    Saves image to disk as a PNG.

    Takes in an array of raw image data.
    """
    raise NotImplementedError


def load_and_decode(file_path: Path) -> RawImage:
    """
    loads an image from disk and decodes it.
    """
    with open(file_path, "rb") as f:
        bitstream = f.read()
        return decode(bitstream)


def load_decode_and_save(file_in: Path, file_out: Path):
    """
    Loads, decodes, and saves the image as a PNG.
    """
    save(file_out, load_and_decode(file_in))


def print_help(exit_code=0):
    """
    Prints out a help message to standard out, then exits.
    """
    print(
        """
        Usage: pyjxl INPUT_FILE [OUTPUT_FILE]
        Decodes the INPUT_FILE, optionally saving to the OUTPUT_FILE.
        
          -h, --help    display this help and exit
        
        pyJXL is intended to decode PPM, JPEG, and JPEG XL files. It outputs to
        a PNG file.
        """)
    exit(exit_code)


if __name__ == "__main__":
    if "-h" in argv or "--help" in argv or not (1 < len(argv) < 3):
        print_help(0)

    file_in = argv[1]
    if len(argv) == 3:
        file_out = argv[2]
        print("Decoding {file_in} and saving to {file_out}...")
        load_decode_and_save(file_in, file_out)
    else:
        print("No output specified!")
        print(f"Decoding {file_in} and discarding output...")
        load_and_decode(file_in)
