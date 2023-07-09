#! /usr/bin/env python3

"""
jxl-strip

Strips the container off of a jxl file, reducing the size and removing any
potentially sensitive metadata. The original file is overwritten, so make sure
to have a copy if you are experimenting.

Currently it is possible for this program to produce invalid JXL files, if the
the image is a level 10 image, in which case the container is required. This
should be uncommon however, and really only effects CMYK, or gigapixel images.
"""

from pathlib import Path
import argparse
import sys


def has_container(bitstream: bytes) -> bool:
    """
    Determines the image type by sniffing the first few bytes.
    """
    # Test for raw JXL codestream.
    if bitstream[:2] == bytes.fromhex("FF0A"):
        return False
    # Test for JXL box structure. http://www-internal/2022/18181-2#box-types
    if bitstream[:12] == bytes.fromhex("0000 000C 4A58 4C20 0D0A 870A"):
        return True
    raise ValueError("Not a JPEG XL file.")


def decode_container(bitstream: bytes) -> bytes:
    """
    Parses the ISOBMFF container, extracts the codestream, and decodes it.
    JXL container specification: http://www-internal/2022/18181-2
    """

    def parse_box(bitstream: bytes, box_start: int) -> dict:
        LBox = int.from_bytes(bitstream[box_start : box_start + 4])
        XLBox = None
        if 1 < LBox <= 8:
            raise ValueError(f"Invalid LBox at byte {box_start}.")
        if LBox == 1:
            XLBox = int.from_bytes(bitstream[box_start + 8 : box_start + 16])
            if XLBox <= 16:
                raise ValueError(f"Invalid XLBox at byte {box_start}.")
        if XLBox:
            header_length = 16
            box_length = XLBox
        else:
            header_length = 8
            if LBox == 0:
                box_length = len(bitstream) - box_start
            else:
                box_length = LBox
        return {
            "length": box_length,
            "type": bitstream[box_start + 4 : box_start + 8],
            "data": bitstream[box_start + header_length : box_start + box_length],
        }

    # Reject files missing required boxes. These two boxes are required to be at
    # the start and contain no values, so we can manually check there presence.
    # Signature box. (Redundant as has already been checked.)
    if bitstream[:12] != bytes.fromhex("0000000C 4A584C20 0D0A870A"):
        raise ValueError("Invalid signature box.")
    # File Type box.
    if bitstream[12:32] != bytes.fromhex(
        "00000014 66747970 6A786C20 00000000 6A786C20"
    ):
        raise ValueError("Invalid file type box.")

    partial_codestream = []
    container_pointer = 32
    while container_pointer < len(bitstream):
        box = parse_box(bitstream, container_pointer)
        container_pointer += box["length"]
        if box["type"] == b"jxll":
            level = int.from_bytes(box["data"])
            if level != 5 or level != 10:
                raise ValueError("Unknown level")
        elif box["type"] == b"jxlc":
            codestream = box["data"]
        elif box["type"] == b"jxlp":
            index = int.from_bytes(box["data"][:4])
            partial_codestream.append([index, box["data"][4:]])

    if partial_codestream:
        partial_codestream.sort(key=lambda i: i[0])
        codestream = b"".join([i[1] for i in partial_codestream])

    return codestream


def main() -> int:
    """Read file from the command line, and strip its box."""

    parser = argparse.ArgumentParser(
        prog="jxl-strip",
        description="Strips the container from a JPEG XL image",
        epilog="jxl-strip will strip the container from any jxl images, reducing their size\nand removing any privacy compromising metadata.",
    )
    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="explain what is happening.",
    )
    parser.add_argument(
        "file", help="JXL file to strip, will be overwritten", type=Path
    )
    args = parser.parse_args()

    # Main program logic start.
    try:
        with open(args.file, "rb") as fp:
            # has_container will raise a ValueError if not a jxl file, and only
            # reading the first 12 bytes makes this check fast. If it is a jxl
            # file, reads the rest of it.
            bitstream = fp.read(12)
            container = has_container(bitstream)
            bitstream = bitstream + fp.read()
        if container:
            # There is technically a race condition here as we are reopening the
            # file, but doing it otherwise is annoying, and it is unlikely that
            # another tool is manipulating the files at the same time.
            if args.verbose:
                print(f"Striping {args.file}", file=sys.stderr)
            with open(args.file, "wb") as fp:
                fp.write(decode_container(bitstream))
        else:
            if args.verbose:
                print(
                    f"Skipping {args.file} as it is already stripped", file=sys.stderr
                )
    except FileNotFoundError:
        print(f"{args.file} not found", sys.stderr)
        return 1
    except ValueError:
        print(f"{args.file} is not a valid JXL file", sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
