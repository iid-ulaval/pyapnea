import seaborn as sns
import matplotlib.pyplot as plt

from src.pyapnea.oscar.oscar_loader import load_session
from src.pyapnea.oscar.oscar_getter import event_data_to_dataframe
from src.pyapnea.oscar.oscar_constants import ChannelID
from src.pyapnea.pytorch.raw_oscar_dataset import RawOscarDataset

# this will read the file and transform it to an internal data structure (see data_structure.py)
oscar_session_data = load_session('test/data/raw/ResMed_1234567890/Events/61f5f33c.001')

# this line takes an internal data structure and transform it into a pandas dataframe
df = event_data_to_dataframe(oscar_session_data=oscar_session_data,
                             channel_ids=[ChannelID.CPAP_FlowRate.value])
print(df)

df = event_data_to_dataframe(oscar_session_data=oscar_session_data,
                             channel_ids=[ChannelID.CPAP_FlowRate.value,
                                          ChannelID.CPAP_Obstructive.value,
                                          ChannelID.CPAP_ClearAirway.value])
print(df)

df.set_index('time_utc', inplace=True)
df.sort_index(inplace=True)
print(df)

print(df[df.ClearAirway.notnull()])

print(df[df.index <= '2022-01-30 02:33:23+00:00'])
print(df[df.index >= '2022-01-30 02:33:23+00:00'])

df = df[(df.index <= '2022-01-30 02:35:23+00:00') & (df.index >= '2022-01-30 02:30:23+00:00')]
sns.lineplot(df['FlowRate'])
plt.savefig("missingvalues.png", format='png')

df = event_data_to_dataframe(oscar_session_data=oscar_session_data,
                             channel_ids=[ChannelID.CPAP_FlowRate.value,
                                          ChannelID.CPAP_Obstructive.value,
                                          ChannelID.CPAP_ClearAirway.value],
                             mis_value_strategy={ChannelID.CPAP_FlowRate.value: 'ignore'})
print(df[df.ClearAirway.notnull()])

dataset = RawOscarDataset(data_path='test/data/raw')
print(dataset[0])  # accessing the first element

dataset = RawOscarDataset(data_path='test/data/raw', getitem_type='dataframe')
print(dataset[0])  # accessing the first element as dataframe

dataset = RawOscarDataset(data_path='test/data/raw',
                          getitem_type='dataframe',
                          channel_ids=[ChannelID.CPAP_Leak.value,
                                       ChannelID.CPAP_FlowRate.value])
print(dataset[0])  # accessing the first element with CPAP_Leak and CPAP_FlowRate
print(dataset[0][dataset[0].ApneaEvent != 0.0])

dataset = RawOscarDataset(data_path='test/data/raw',
                          getitem_type='dataframe',
                          channel_ids=[ChannelID.CPAP_Leak.value,
                                       ChannelID.CPAP_FlowRate.value],
                          output_events_merged=[ChannelID.CPAP_Obstructive.value])
print(dataset[0][dataset[0].ApneaEvent != 0.0])

print(len(dataset))

