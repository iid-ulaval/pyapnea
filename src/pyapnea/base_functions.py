import struct
from typing import Any


def binary(num: float) -> str:
    """
    Transform a number to a binary format as string (3 => '00000011')

    Args:
        num: number to transform

    Returns:
        String representing `num`
    """
    return ''.join('{:0>8b}'.format(c) for c in struct.pack('!f', num))


def _debug_individual_unpack(buffer, formt, position):
    """ display individual unpacked values."""
    print('from', position,
          'to', position + struct.calcsize(formt),
          'size', struct.calcsize(formt),
          'of ', formt,
          'raw bytes ', buffer[position:position + struct.calcsize(formt)].hex(),
          'values ', struct.unpack_from(formt, buffer, offset=position))
    p = position
    # do not display for string reading
    if 's' not in formt:
        for e in formt:
            if e not in ['<', '>']:
                print(' element format', e,
                      'from', p,
                      'to', p + struct.calcsize(e),
                      'size', struct.calcsize(e),
                      'raw bytes ', buffer[p:p + struct.calcsize(e)].hex(),
                      'value', struct.unpack_from(e, buffer, offset=p))
                p = p + struct.calcsize(e)


def unpack(buffer: bytes, formt: str, position: int) -> tuple[int, tuple[Any, ...]]:
    """
    Unpack a number of values from buffer beginning at position.

    Args:
        buffer: Buffer to extract values.
        formt: values format from struct package.
        position: position to begin.

    Returns:
        New unread position after extract the fields and tuple of fields.
    """
    return position + struct.calcsize(formt), struct.unpack_from(formt, buffer, offset=position)
