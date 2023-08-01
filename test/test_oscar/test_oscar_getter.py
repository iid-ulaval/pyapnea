from unittest import TestCase
from datetime import datetime, timezone

from src.pyapnea.oscar.oscar_loader import load_session
from src.pyapnea.oscar.oscar_getter import get_channel_from_code, event_data_to_dataframe
from src.pyapnea.oscar.oscar_constants import ChannelID


class TestOscarSessionGetter(TestCase):

    def test_get_channel_from_code(self):
        filename = '../data/63c6e928.001'
        oscar_session_data = load_session(filename)
        real_channel = get_channel_from_code(oscar_session_data, ChannelID.CPAP_Te.value)
        expected_channel = oscar_session_data.data.channels[0]

        self.assertEqual(expected_channel, real_channel)

    def test_data_to_dataframe(self):
        filename = '../data/63c6e928.001'
        oscar_session_data = load_session(filename)
        df = event_data_to_dataframe(oscar_session_data, [ChannelID.CPAP_Te.value])

        self.assertListEqual(['time_utc', 'Te'], df.columns.to_list())
        self.assertEqual(26 * 0.019999999552965164, df.loc[0, 'Te'])
        expected_date = datetime(2023, 1, 17, 18, 30, 5, 440000, tzinfo=timezone.utc)
        self.assertEqual(expected_date, df.loc[0, 'time_utc'].to_pydatetime())

    def test_data_to_dataframe_multiple_channels(self):
        filename = '../data/63c6e928.001'
        oscar_session_data = load_session(filename)
        df = event_data_to_dataframe(oscar_session_data, [ChannelID.CPAP_Te.value, ChannelID.CPAP_FlowRate.value])

        self.assertListEqual(['time_utc', 'Te', 'FlowRate'], df.columns.to_list())
        self.assertEqual(26 * 0.019999999552965164, df.loc[0, 'Te'])
        self.assertEqual(-6.120000243186951, df.loc[0, 'FlowRate'])
        expected_date = datetime(2023, 1, 17, 18, 30, 5, 440000, tzinfo=timezone.utc)
        self.assertEqual(expected_date, df.loc[0, 'time_utc'].to_pydatetime())

    def test_data_to_dataframe_no_channel_found(self):
        filename = '../data/63c6e928.001'
        oscar_session_data = load_session(filename)
        df = event_data_to_dataframe(oscar_session_data, [ChannelID.CPAP_AllApnea.value])
        self.assertListEqual(['no_channel'], df.columns.to_list())

    def test_data_to_dataframe_empty_channel_list(self):
        filename = '../data/63c6e928.001'
        oscar_session_data = load_session(filename)
        df = event_data_to_dataframe(oscar_session_data, [])
        self.assertListEqual(['no_channel'], df.columns.to_list())

    def test_data_to_dataframe_multiple_events(self):
        filename = '../data/61f5f33c.001'
        oscar_session_data = load_session(filename)
        flowrate_channel = get_channel_from_code(oscar_session_data, ChannelID.CPAP_FlowRate.value)

        # ensure the correct input
        self.assertEqual(2, len(flowrate_channel.events))

        nb_flowrate_points = sum([evt.evcount for evt in flowrate_channel.events])

        df = event_data_to_dataframe(oscar_session_data, [ChannelID.CPAP_FlowRate.value])

        self.assertEqual(nb_flowrate_points, len(df))
        self.assertFalse(df['FlowRate'].isna().any())

    def test_data_to_dataframe_multiple_events_multiple_channels_ignore_nan(self):
        filename = '../data/61f5f33c.001'
        oscar_session_data = load_session(filename)
        flowrate_channel = get_channel_from_code(oscar_session_data, ChannelID.CPAP_FlowRate.value)

        # ensure the correct input
        self.assertEqual(2, len(flowrate_channel.events))

        nb_flowrate_points = sum([evt.evcount for evt in flowrate_channel.events])

        df = event_data_to_dataframe(oscar_session_data,
                                     [ChannelID.CPAP_ClearAirway.value,
                                      ChannelID.CPAP_FlowRate.value],
                                     {ChannelID.CPAP_FlowRate.value: 'ignore'})

        self.assertEqual(nb_flowrate_points, len(df))
        self.assertFalse(df['FlowRate'].isna().any())

    def test_data_to_dataframe_multiple_events_multiple_channels_replace_nan(self):
        filename = '../data/61f5f33c.001'
        oscar_session_data = load_session(filename)
        flowrate_channel = get_channel_from_code(oscar_session_data, ChannelID.CPAP_FlowRate.value)

        # ensure the correct input
        self.assertEqual(2, len(flowrate_channel.events))

        nb_flowrate_points = sum([evt.evcount for evt in flowrate_channel.events])

        df = event_data_to_dataframe(oscar_session_data,
                                     [ChannelID.CPAP_ClearAirway.value,
                                      ChannelID.CPAP_FlowRate.value],
                                     {ChannelID.CPAP_FlowRate.value: -1000.0})

        self.assertEqual(nb_flowrate_points+1, len(df))
        self.assertFalse(df['FlowRate'].isna().any())