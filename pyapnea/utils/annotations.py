import numpy as np
import pandas as pd

from pyapnea.oscar.oscar_constants import CHANNELS, ChannelID


def generate_annotations(df: pd.DataFrame, length_event=None, output_events_merge=None):
    """
    Generate annotations from a dataframe containing annotation at one point only.

    Args:
        df: source dataframe used to generate annotation.
        length_event: length of the events to complete annotations. format in Offset aliases. \
                        None for keeping annotation as-is (default).
        output_events_merge: list of ChannelID (not value of ChannelID) to merge to become the ApneaEvent. None for all apnea events

    Returns:
        A copy of the dataframe with annotations added inside a 'ApneaEvent' column.
    """
    result = df.copy()
    if output_events_merge:
        possible_apnea_events = output_events_merge
    else:
        possible_apnea_events = [ChannelID.CPAP_ClearAirway, ChannelID.CPAP_Obstructive, ChannelID.CPAP_Hypopnea,
                                 ChannelID.CPAP_Apnea]
    possible_apnea_events_str = [c[5] for c in CHANNELS if c[1] in possible_apnea_events]
    events_in_origin = [i for i in result.columns if i in possible_apnea_events_str]
    if len(events_in_origin) == 0:
        result['ApneaEvent'] = 0.0
    else:
        result['ApneaEvent'] = result[events_in_origin].sum(axis=1)
        result['ApneaEvent'] = result['ApneaEvent'].apply(lambda x: 1 if (not pd.isnull(x)) and (x != 0) else np.nan)
        result.fillna({'ApneaEvent': 0}, inplace=True)
        if length_event is not None:
            list_index_annot = result.index[result['ApneaEvent'] == 1].tolist()
            for annot_index in list_index_annot:
                indexes = result.index[((result.index <= annot_index) &
                                        (result.index >= (annot_index - pd.to_timedelta(length_event))))]
                result.loc[indexes, 'ApneaEvent'] = 1

    return result


def is_contain_event(element, output_type='dataframe'):
    """
    Compute whether an element contains at least on event

    Args:
        element: element to consider
        output_type: 'dataframe' : an element is a dataframe containing at least the 'ApneaEvent' column
                     'numpy' : an element is a tuple (x, y)

    Returns:
        True if the element of a dataset contains at least one event
    """
    if output_type == 'dataframe':
        return 1.0 in element['ApneaEvent'].values
    else:
        return 1.0 in element[1]


def get_nb_events(dataset):
    """
    Get the number of element of a dataset that contain at least one apnea event

    Returns:
        A tuple containing (number of events, list of all events)
    """

    events = [is_contain_event(element, dataset.getitem_type) for element in dataset]
    nb_contain_event = events.count(True)
    return nb_contain_event, events
