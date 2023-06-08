"""
pyjxl module

This module implements the core code of pyJXL.
"""

from pathlib import Path
import sys

from jxl_decode.common import RawImage
from jxl_decode.decode_ppm import decode_ppm
from jxl_decode.decode_jpg import decode_jpg
from jxl_decode.decode_jxl import decode_jxl
from jxl_decode.encode_png import encode_png


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


def save(filename: Path, image: RawImage):
    """Saves image to disk as a PNG."""
    png = encode_png(image)
    with open(filename, "wb") as f:
        f.write(png)


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


def print_help(exit_code=0):
    """
    Prints out a help message to standard out, then exits.
    """
    print("""Usage: pyjxl INPUT_FILE [OUTPUT_FILE]
Decodes the INPUT_FILE, optionally saving to the OUTPUT_FILE.

-h, --help    display this help and exit

pyJXL is intended to decode PPM, JPEG, and JPEG XL files, outputting a PNG.""")
    sys.exit(exit_code)


def main():
    """Command line handling."""
    if "-h" in sys.argv or "--help" in sys.argv or not 1 < len(sys.argv) <= 3:
        print_help(0)
    file_in = Path(sys.argv[1])
    if len(sys.argv) == 3:
        file_out = Path(sys.argv[2])
        print(f"Decoding {file_in} and saving to {file_out}...")
        save(file_out, decode(load(file_in)))
    else:
        print(f"Decoding {file_in} and printing output...")
        print(decode(load(file_in)))
