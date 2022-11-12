"""
JPEG XL Decoder
"""

from pyjxl.common import RawImage


def decode_jxl(bitstream: bytearray) -> RawImage:
    """
    JXL specification: http://www-internal/2022/18181-1
    """
    raise NotImplementedError
