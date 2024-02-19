import os.path
from typing import List, Optional
from os import listdir
from os.path import isfile, join, isdir

from pyapnea.oscar.oscar_constants import ChannelID
from pyapnea.oscar.oscar_getter import event_data_to_dataframe
from pyapnea.oscar.oscar_loader import load_session
from torch.utils.data import Dataset

from pyapnea.utils.annotations import generate_annotations


class RawOscarDataset(Dataset):

    def __init__(self,
                 data_path: str,
                 getitem_type: str = 'numpy',
                 limits: slice = None,
                 output_events_merged: Optional[List[ChannelID]] = None,
                 channel_ids: Optional[List[ChannelID]] = None):
        """
        Torch dataset for handling raw OSCAR data.
        This class generates annotations within 1Os before the end of the apnea event.

        Args:
            data_path: the data path of the OSCAR data. The path must contain the directory of all CPAP machine.
            getitem_type: The type of one element obtained by []. Can be 'numpy' or 'dataframe'.
            limits: slice to filter the dataset. None means no limit.
            output_events_merged: List of apnea events (ChannelID) to merge into the 'ApneaEvent' column, None means all apnea event types are merged
            channel_ids: List of channel to get. If None, only CPAP_FlowRate is get.
        """
        self.getitem_type = getitem_type
        list_machines = [d for d in listdir(data_path) if isdir(os.path.join(data_path, d))]
        data_path_cpap = [os.path.join(data_path, d, 'Events') for d in list_machines]
        data_path_cpap1 = data_path_cpap[0]
        self.list_files = [{'label': f, 'value': f, 'fullpath': join(data_path_cpap1, f)} for f in
                           listdir(data_path_cpap1)
                           if isfile(join(data_path_cpap1, f))]

        if len(data_path_cpap) == 2:
            data_path_cpap2 = data_path_cpap[1]

            self.list_files.extend(
                [{'label': f, 'value': f, 'fullpath': join(data_path_cpap2, f)} for f in listdir(data_path_cpap2) if
                 isfile(join(data_path_cpap2, f))])

        if limits is not None:
            self.list_files = self.list_files[limits]

        self.list_files = sorted(self.list_files, key=lambda x: x['fullpath'])

        if channel_ids is not None:
            self.channel_ids = channel_ids
        else:
            self.channel_ids = [ChannelID.CPAP_FlowRate.value]

        self.output_events_merged = output_events_merged

    def __len__(self):
        return len(self.list_files)

    def __getitem__(self, idx):
        result = None
        oscar_session_data = load_session(self.list_files[idx]['fullpath'])
        channel_to_get = [ChannelID.CPAP_Obstructive.value,  # Apnée obstructive
                          ChannelID.CPAP_ClearAirway.value,  # Apnée centrale
                          ChannelID.CPAP_Hypopnea.value,  # Hypopnée
                          ChannelID.CPAP_Apnea.value,  # Non déterminé
                          ]
        channel_to_get.extend(self.channel_ids)
        df = event_data_to_dataframe(oscar_session_data,
                                     channel_ids=channel_to_get,
                                     mis_value_strategy={ChannelID.CPAP_FlowRate.value: 'ignore'})

        df.set_index('time_utc', inplace=True)
        df.sort_index(inplace=True)
        df = generate_annotations(df, length_event='10S', output_events_merge=self.output_events_merged)

        if self.getitem_type == 'numpy':
            result = df[['FlowRate']].to_numpy(), df[['ApneaEvent']].to_numpy()
        if self.getitem_type == 'dataframe':
            result = df
        return result
