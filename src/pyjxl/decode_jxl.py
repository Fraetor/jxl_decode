"""
JPEG XL Decoder
"""

from pyjxl.common import RawImage


def decode_jxl(bitstream: bytearray) -> RawImage:
    """
    Decodes a JPEG XL image.
    """
    if bitstream[:2] == bytes.fromhex("FF0A"):
        image = decode_codestream(bitstream)
    else:
        image = decode_container(bitstream)
    return image


def decode_codestream(codestream: bytearray) -> RawImage:
    """
    Decodes the actual codestream.
    JXL codestream specification: http://www-internal/2022/18181-1
    """
    print("Codestream:", codestream.hex(" ", 4))
    raise NotImplementedError


def decode_container(bitstream: bytearray) -> RawImage:
    """
    Parses the ISOBMFF container, extracts the codestream, and decodes it.
    JXL container specification: http://www-internal/2022/18181-2
    """
    def parse_box(bitstream: bytearray, box_start: int) -> dict:
        LBox = int.from_bytes(bitstream[box_start:box_start+4])
        XLBox = None
        if 1 < LBox <= 8:
            raise ValueError(f"Invalid LBox at byte {box_start}.")
        if LBox == 1:
            XLBox = int.from_bytes(bitstream[box_start+8:box_start+16])
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
            "type": bitstream[box_start+4:box_start+8],
            "data": bitstream[box_start+header_length:box_start+box_length]
        }

    # Reject files missing required boxes. These two boxes are required to be at
    # the start and contain no values, so we can manually check there presence.
    # Signature box. (Redundant as has already been checked.)
    if bitstream[:12] != bytes.fromhex("0000000C 4A584C20 0D0A870A"):
        raise ValueError("Invalid signature box.")
    # File Type box.
    if bitstream[12:32] != bytes.fromhex("00000014 66747970 6A786C20 00000000 6A786C20"):
        raise ValueError("Invalid file type box.")

    partial_codestream = []
    container_pointer = 32
    while container_pointer < len(bitstream):
        box = parse_box(bitstream, container_pointer)
        container_pointer += box["length"]
        match box["type"]:
            case b'jxll':
                level = int.from_bytes(box["data"])
                if level != 5 or level != 10:
                    raise ValueError("Unknown level")
            case b'jxlc':
                codestream = box["data"]
            case b'jxlp':
                index = int.from_bytes(box["data"][:4])
                partial_codestream.append([index, box["data"][4:]])
            case b'jxli':
                # Frame Index box. It could be useful to parse?
                # http://www-internal/2022/18181-2#toc17
                pass

    if partial_codestream:
        partial_codestream.sort(key=lambda i: i[0])
        codestream = b''.join([i[1] for i in partial_codestream])

    image = decode_codestream(codestream)
    return image
