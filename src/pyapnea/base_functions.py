import struct


def binary(num):
    """ transform a number to a binary format as string (3 => '00000011')"""
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


def unpack(buffer, formt, position):
    """
    Unpack a number of values from buffer beginning at position.
    :param buffer: Buffer to extract values.
    :param formt: values format from struct package.
    :param position: position to begin.
    :return: new unread position after extract the fields and tuple of fields.
    """
    return position + struct.calcsize(formt), struct.unpack_from(formt, buffer, offset=position)
