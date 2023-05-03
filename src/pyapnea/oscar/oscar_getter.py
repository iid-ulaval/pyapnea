import pandas as pd

from .oscar_constants import CHANNELS


def get_channel_from_code(oscar_session_data, channel_id):
    """
    Get channel data inside OSCARSession data structure from a channel_id
    :param oscar_session_data: OSCARSession filled from file
    :param channel_id: one channel id (see channelID in oscar_constants.py)
    :return: channel data or None if the channelID is not found
    """
    list_result = [item for item in oscar_session_data.data.channels if item.code == channel_id]
    if len(list_result) > 0:
        return list_result[0]
    else:
        return None


def event_data_to_dataframe(oscar_session_data, channel_id):
    """
    get the event data as dataframe of an OSCARSession from a channelID
    :param oscar_session_data: OSCARSession filled from file
    :param channel_id: one channel id (see channelID in oscar_constants.py)
    :return: a dataframe with the following columns :
             "time",  "time_absolute".
             "data", "data2" (if exists),
             ChannelID text, ChannelID text +"2" (see oscar_constants.py)
             if the channelID is not found, return an empty dataframe containing
             2 columns "time_absolute" and  ChannelID text
    """
    channel = get_channel_from_code(oscar_session_data, channel_id)
    y_col_name = [c[5] for c in CHANNELS if c[1].value == channel_id][0]
    if channel is not None:
        gain = channel.events[0].gain
        if channel.events[0].t8 == 0:
            channel.events[0].time = range(0, channel.events[0].evcount * int(channel.events[0].rate),
                                           int(channel.events[0].rate))
        df = pd.DataFrame(data={'time': channel.events[0].time,
                                'data': channel.events[0].data})
        df[y_col_name] = df['data'] * gain

        if channel.events[0].second_field:
            # not tested because do not have 2nd field in files
            df['data2'] = channel.events[0].data2
            df[y_col_name + '2'] = df['data2'] * gain

        df['time_absolute'] = df['time'] + channel.events[0].ts1
        df['time_absolute'] = pd.to_datetime(df['time_absolute'], unit='ms')

    else:
        df = pd.DataFrame(data={'time_absolute': [],
                                y_col_name: []})
    return df
