from typing import Union, List, Any

import pandas as pd

from .oscar_constants import CHANNELS
from .data_structure import OSCARSession, OSCARSessionChannel


def get_channel_from_code(oscar_session_data: OSCARSession, channel_id: int) -> Union[OSCARSessionChannel, None]:
    """
    Get channel data inside OSCARSession data structure from a channel_id

    Args:
        oscar_session_data: OSCARSession filled from file
        channel_id: one channel id (.value, see channelID in oscar_constants.py)

    Returns:
        Channel data (`OSCARSessionChannel`) or None if the channelID is not found in the session
    """
    list_result = [item for item in oscar_session_data.data.channels if item.code == channel_id]
    if len(list_result) > 0:
        return list_result[0]
    else:
        return None


def event_data_to_dataframe(oscar_session_data: OSCARSession, channel_ids: List[Any]) -> pd.DataFrame:
    """
    Get the event data as dataframe of an OSCARSession from a channelID.

    Args:
        oscar_session_data: OSCARSession filled from file
        channel_ids: List of channel id (see channelID in oscar_constants.py)

    Returns:
        A dataframe with the following columns : ["time",  "time_utc", \
         ChannelID text, ChannelID text +"2", ... (see oscar_constants.py) ]. \
        if no channel_ids are found, return an empty dataframe containing \
        one column named 'no_channel'
    """
    global_df = pd.DataFrame(columns=['no_channel'])
    for channel in oscar_session_data.data.channels:
        if channel.code in channel_ids:
            y_col_name = [c[5] for c in CHANNELS if c[1].value == channel.code][0]
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

            df['time_utc'] = df['time'] + channel.events[0].ts1
            df['time_utc'] = pd.to_datetime(df['time_utc'], unit='ms')
            df['time_utc'] = df['time_utc'].dt.tz_localize('UTC')

            # deleting no gain columns and relative time
            df.drop(['time', 'data', 'data2'], axis=1, inplace=True, errors='ignore')

            # reordering columns 'time_utc at first
            temp_cols = df.columns.tolist()
            new_cols = temp_cols[-1:] + temp_cols[:-1]
            df = df[new_cols]

            if global_df.empty:
                global_df = df
            else:
                global_df = pd.merge(global_df, df, on='time_utc', how='outer', suffixes=('', '_DROP')).filter(
                    regex='^(?!.*_DROP)')
    return global_df
