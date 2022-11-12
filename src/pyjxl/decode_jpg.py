"""
JPEG JFIF Decoder
"""

from pyjxl.common import RawImage


def decode_jpg(bitstream: bytearray) -> RawImage:
    """
    https://en.wikipedia.org/wiki/JPEG_File_Interchange_Format#File_format_structure
    https://www.w3.org/Graphics/JPEG/jfif3.pdf
    """
    raise NotImplementedError
