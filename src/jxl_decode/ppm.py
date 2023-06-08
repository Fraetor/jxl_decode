"""
PPM decoder and encoder

PPM specification: http://davis.lbl.gov/Manuals/NETPBM/doc/ppm.html

Approx spec: (space can be any ASCII whitespace.)
P6 WIDTH HEIGHT MAXVAL DATA...

DATA scans top to bottom, left to right. E.g:
RGB1 RGB2 RGB3
RGB4 RGB5 RGB6
RGB7 RGB8 RGB9
"""

from jxl_decode.common import RawImage


def decode_ppm(bitstream: bytes) -> RawImage:
    """Creates an image from a PPM bitstream."""
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
                h_strip.append(data[3 * x * y + 3 * x])
            image.ch0.extend(h_strip)

        for y in range(image.height):
            h_strip = []
            for x in range(image.width):
                h_strip.append(data[3 * x * y + 3 * x + 1])
            image.ch1.extend(h_strip)

        for y in range(image.height):
            h_strip = []
            for x in range(image.width):
                h_strip.append(data[3 * x * y + 3 * x + 2])
            image.ch2.extend(h_strip)
    else:
        image.bitdepth = 16
        # PPM is big endian, so from_bytes works by default.
        for y in range(image.height):
            h_strip = []
            for x in range(image.width):
                h_strip.append(
                    int.from_bytes(data[6 * x * y + 6 * x : 6 * x * y + 6 * x + 2])
                )
            image.ch0.extend(h_strip)

        for y in range(image.height):
            h_strip = []
            for x in range(image.width):
                h_strip.append(
                    int.from_bytes(data[6 * x * y + 6 * x + 2 : 6 * x * y + 6 * x + 4])
                )
            image.ch1.extend(h_strip)

        for y in range(image.height):
            h_strip = []
            for x in range(image.width):
                h_strip.append(
                    int.from_bytes(data[6 * x * y + 6 * x + 4 : 6 * x * y + 6 * x + 6])
                )
            image.ch2.extend(h_strip)

    return image


def encode_ppm(image: RawImage) -> bytes:
    """Creates a ppm bitstream from an image."""
    raise NotImplementedError
