from typing import Union, List, Any, Dict, Optional

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


def event_data_to_dataframe(oscar_session_data: OSCARSession,
                            channel_ids: List[Any],
                            mis_value_strategy: Optional[Dict[str, Union[str, float]]] = None) -> pd.DataFrame:
    """
    Get the event data as dataframe of an OSCARSession from channelIDs.

    Args:
        oscar_session_data: OSCARSession filled from file
        channel_ids: List of channel id (see channelID in oscar_constants.py)
        mis_value_strategy: Strategy to deal with missing value on one channel.

            - None : nothing is done, missing values are kept as nan
            - Dictionary containing a channel id as key and a strategy as value:
                * 'ignore' : remove rows where the channel is nan
                * `float` : replace NaN value in the channel by the float value


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
            df_channel = pd.DataFrame(columns=['no_event'])
            for evt in channel.events:
                gain = evt.gain
                if evt.t8 == 0:
                    evt.time = range(0, evt.evcount * int(evt.rate), int(evt.rate))
                df = pd.DataFrame(data={'time': evt.time,
                                        'data': evt.data})
                df[y_col_name] = df['data'] * gain

                if evt.second_field:
                    # not tested because do not have 2nd field in files
                    df['data2'] = evt.data2
                    df[y_col_name + '2'] = df['data2'] * gain

                df['time_utc'] = df['time'] + evt.ts1
                df['time_utc'] = pd.to_datetime(df['time_utc'], unit='ms')
                df['time_utc'] = df['time_utc'].dt.tz_localize('UTC')

                # deleting no gain columns and relative time
                df.drop(['time', 'data', 'data2'], axis=1, inplace=True, errors='ignore')

                # reordering columns 'time_utc at first
                temp_cols = df.columns.tolist()
                new_cols = temp_cols[-1:] + temp_cols[:-1]
                df = df[new_cols]

                if df_channel.empty:
                    df_channel = df
                else:
                    df_channel = pd.concat([df_channel, df])

            if global_df.empty:
                global_df = df_channel
            else:
                global_df = pd.merge(global_df, df_channel, on='time_utc', how='outer', suffixes=('', '_DROP')).filter(
                    regex='^(?!.*_DROP)')

            # apply missing value strategies
            if mis_value_strategy:
                for channel, strategy in mis_value_strategy.items():
                    col_name = [c[5] for c in CHANNELS if c[1].value == channel][0]
                    if col_name in global_df.columns:
                        if strategy == 'ignore':
                            global_df = global_df[global_df[col_name].notnull()]
                        if isinstance(strategy, float):
                            global_df[col_name].fillna(strategy, inplace=True)
    return global_df
