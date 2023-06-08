"""
This module implements the core code of jxl_decode, from which other modules are
called.
"""

from pathlib import Path
import logging

from jxl_decode.common import RawImage
from jxl_decode.ppm import decode_ppm, encode_ppm
from jxl_decode.jpg import decode_jpg
from jxl_decode.jxl import decode_jxl


def load(file_path: Path) -> bytes:
    """Loads an image from disk and returns it."""
    with open(file_path, "rb") as fp:
        return fp.read()


def save(filename: Path, image: RawImage):
    """Saves image to disk as a PPM."""
    png = encode_ppm(image)
    with open(filename, "wb") as fp:
        fp.write(png)


def sniff_image_type(bitstream: bytes) -> str:
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
    if bitstream[:2] == b"P6":
        return "ppm"
    # Test for JPEG/JFIF.
    if bitstream[:2] == bytes.fromhex("FFD8"):
        return "jpg"
    raise ValueError("Not a recognised image type.")


def decode(bitstream: bytes) -> RawImage:
    """Decodes a bitstream using the appropriate decoder."""
    match sniff_image_type(bitstream[:12]):
        case "jxl":
            return decode_jxl(bitstream)
        case "jpg":
            return decode_jpg(bitstream)
        case "ppm":
            return decode_ppm(bitstream)


def cli_entrypoint():
    """Command line handling."""
    import argparse

    parser = argparse.ArgumentParser(
        prog="jxl_decode",
        description="Decodes a JPEG XL image",
        epilog="jxl_decode is intended to decode PPM, JPEG, and JPEG XL files, outputting a PPM.",
    )
    parser.add_argument(
        "-v",
        "--verbose",
        action="count",
        default=0,
        help="explain what is happening. Can be given multiple times",
    )
    parser.add_argument("input_file", help="file to decode", type=Path)
    parser.add_argument("output_file", nargs="?", type=Path, default=None)
    args = parser.parse_args()

    # Set logging verbosity
    if args.verbose >= 2:
        logging.basicConfig(level=logging.DEBUG)
    elif args.verbose >= 1:
        logging.basicConfig(level=logging.INFO)
    else:
        logging.basicConfig(level=logging.WARNING)

    if args.output_file:
        logging.info(f"Decoding {args.input_file} and saving to {args.output_file}...")
        save(args.output_file, decode(load(args.input_file)))
    else:
        logging.info(f"Decoding {args.input_file} and printing output...")
        print(decode(load(args.input_file)))
