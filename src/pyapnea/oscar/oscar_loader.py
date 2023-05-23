from .data_structure import OSCARSessionHeader, OSCARSession, OSCARSessionData, OSCARSessionChannel, OSCARSessionEvent
from ..base_functions import unpack


def read_session_header(buffer: bytes, position: int) -> tuple[int, OSCARSessionHeader]:
    """
    Read the header of an OSCAR session file. Only support version >= 10 at the moment.

    Args:
        buffer: Buffer containing the header data
        position: Position of the header in the buffer

    Returns:
        New position after header data in buffer and an `OSCARSessionHeader` data structure
    """
    header_data = OSCARSessionHeader()
    position, (magicnum, version, typ, machid, sessid, s_first, s_last) = unpack(buffer, 'IHHIIqq', position)
    header_data.magicnumber = magicnum
    header_data.version = version
    header_data.filetype = typ
    header_data.deviceid = machid
    header_data.sessionid = sessid
    header_data.sfirst = s_first
    header_data.slast = s_last

    if version >= 10:
        position, (compmethod, machtype, datasize, crc16) = unpack(buffer, 'HHIH', position)
        header_data.compmethod = compmethod
        header_data.machtype = machtype
        header_data.datasize = datasize
        header_data.crc16 = crc16
    else:
        print('VERSION NOT SUPPORTED')

    return position, header_data


def read_event_metadata(buffer: bytes, position: int) -> tuple[int, OSCARSessionEvent]:
    """
    Read one event metadata of an OSCAR session file.

    Args:
        buffer: buffer containing the session data
        position: position of the current event metadata

    Returns:
        New position after current event metadata in buffer and an OSCARSessionEvent data structure
    """
    position, (ts1, ts2, evcount, t8, rate, gain, offset, mn, mx, len_dim) = unpack(buffer,
                                                                                    '<qqiBdddddi',
                                                                                    position)
    event_data = OSCARSessionEvent()
    event_data.ts1 = ts1
    event_data.ts2 = ts2
    event_data.evcount = evcount
    event_data.t8 = t8
    event_data.rate = rate
    event_data.gain = gain
    event_data.offset = offset
    event_data.mn = mn
    event_data.mx = mx
    event_data.len_dim = len_dim
    # See QT QDataStream.cpp QDataStream &QDataStream::readBytes(char *&s, uint &l)
    # not totally sure about this but seems to work with signed int length
    if len_dim != -1:
        position, (dim,) = unpack(buffer, str(len_dim) + 's', position)
        event_data.dim = dim.decode('UTF-16-LE')
    else:
        event_data.dim = ''
    position, (second_field,) = unpack(buffer, '?', position)
    event_data.second_field = second_field

    if second_field:
        position, (mn2, mx2) = unpack(buffer, 'ff', position)
        event_data.mn2 = mn2
        event_data.mx2 = mx2

    return position, event_data


def read_channel_metadata(buffer: bytes, position: int) -> tuple[int, OSCARSessionChannel]:
    """
    Read metadata of a channel in an OSCAR session file.

    Args:
        buffer: buffer containing the session data
        position: position of the current channel metadata

    Returns:
        New position after current channel metadata in buffer and an OSCARSessionChannel data structure
    """
    position, (code,) = unpack(buffer, 'I', position)
    position, (size2,) = unpack(buffer, 'h', position)
    channel_data = OSCARSessionChannel()
    # Codes are described in oscar_constants.cpp
    channel_data.code = code
    channel_data.size2 = size2
    for evt in range(size2):
        position, event_data = read_event_metadata(buffer, position)
        channel_data.events.append(event_data)
    return position, channel_data


def read_channel_data(buffer: bytes,
                      position: int,
                      data_data: OSCARSessionData,
                      channel_num: int) -> tuple[int, OSCARSessionChannel]:
    """
    Read data of one channel of an OSCAR session file.

    Args:
        buffer: buffer containing the session data
        position: position of the channel to read
        data_data: OSCARSessionData structure already filled with other metadata
        channel_num: id of channel to read

    Returns:
        New position after the channel data and the OSCARSessionChannel data structure
    """
    channel_data = data_data.channels[channel_num]
    for evt_id in range(channel_data.size2):
        event_data = channel_data.events[evt_id]
        # 's' is not correct since it interprets as char
        position, data = unpack(buffer, 'h' * event_data.evcount, position)
        event_data.data = list(data)
        if event_data.second_field:
            position, data2 = unpack(buffer, 'h' * event_data.evcount, position)
            event_data.data2 = list(data2)
        if event_data.t8 != 0:
            position, time_data = unpack(buffer, 'I' * event_data.evcount, position)
            event_data.time = list(time_data)
    return position, channel_data


def read_session_data(buffer: bytes, position: int) -> tuple[int, OSCARSessionData]:
    """
    Read the session data of an OSCAR session file.

    Args:
        buffer: buffer containing the session data
        position: position of the session data in the buffer

    Returns:
        New position after session data in buffer and an OSCARSessionData data structure
    """
    data_data = OSCARSessionData()
    position, (mcsize,) = unpack(buffer, 'h', position)
    data_data.mcsize = mcsize
    for c in range(mcsize):
        position, channel_data = read_channel_metadata(buffer, position)
        data_data.channels.append(channel_data)
    for c in range(mcsize):
        position, channel_data = read_channel_data(buffer, position, data_data, c)
    return position, data_data


def read_session(buffer: bytes, position: int) -> tuple[int, OSCARSession]:
    """
    Read a session of an OSCAR session file. Only support version >= 10 at the moment.

    Args:
        buffer: buffer containing the session
        position: position of the session in the buffer

    Returns:
        New position after session in buffer and an OSCARSession data structure
    """
    databytes = None
    compmethod = 0
    # Header
    position, oscar_session_header = read_session_header(buffer, position)

    temp = buffer[position:]

    if oscar_session_header.version >= 10:
        if compmethod > 0:
            print('COMPRESSION NOT SUPPORTED YET')
        else:
            databytes = temp
    else:
        print('VERSION NOT SUPPORTED')

    dataposition = 0
    dataposition, oscar_session_data = read_session_data(databytes, dataposition)

    oscar_session = OSCARSession()
    oscar_session.header = oscar_session_header
    oscar_session.data = oscar_session_data

    return position, oscar_session


def load_session(filename: str) -> OSCARSession:
    """
    Load an OSCAR session file (.001)

    Args:
        filename: full path of the file including filename

    Returns:
        An OSCARSession instance containing data from file
    """
    with open(filename, mode='rb') as file:
        data = file.read()
        position = 0
        position, oscar_session_data = read_session(data, position)
    return oscar_session_data
