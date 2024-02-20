from unittest import TestCase

import numpy as np
import pandas as pd

from pyapnea import ChannelID
from pyapnea.utils.annotations import generate_annotations


class TestAnnotation(TestCase):

    def test_generate_annotation_keep(self):
        np.random.seed(10)

        rows, cols = 9, 1
        data = np.random.randint(0, 2, size=(rows, cols))
        tidx = pd.date_range('2019-01-01', periods=rows, freq='S')
        original_df = pd.DataFrame(data,
                                   columns=['Obstructive'], index=tidx)

        result_df = generate_annotations(original_df)

        assert (result_df['Obstructive'].isin([0, 1]).sum(axis=0) == len(result_df))
        assert (result_df['Obstructive'].to_list() == original_df['Obstructive'].to_list())
        assert (result_df['ApneaEvent'].to_list() == result_df['Obstructive'].to_list())

    def test_generate_annotation_1_nan(self):
        np.random.seed(10)

        rows, cols = 6, 1
        data = [np.nan, 10, np.nan, np.nan, 0.5, np.nan]
        tidx = pd.date_range('2019-01-01', periods=rows, freq='S')
        original_df = pd.DataFrame(data,
                                   columns=['Obstructive'], index=tidx)

        result_df = generate_annotations(original_df)

        assert result_df['Obstructive'].equals(original_df['Obstructive'])
        assert result_df['ApneaEvent'].to_list() == [0, 1, 0, 0, 1, 0]

    def test_generate_annotation_no_event(self):
        np.random.seed(10)

        rows, cols = 6, 1
        data = np.random.randint(0, 2, size=(rows, cols))
        tidx = pd.date_range('2019-01-01', periods=rows, freq='S')
        original_df = pd.DataFrame(data,
                                   columns=['FlowRate'], index=tidx)

        result_df = generate_annotations(original_df)

        assert (result_df['ApneaEvent'].isin([0, 1]).sum(axis=0) == len(result_df))
        assert (result_df['ApneaEvent'].to_list() == ([0.0] * rows))
        assert result_df.columns.tolist() == ['FlowRate', 'ApneaEvent']

    def test_generate_annotation_entire_event(self):
        np.random.seed(10)

        rows, cols = 20, 1
        data = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 23, 0]
        tidx = pd.date_range('2019-01-01', periods=rows, freq='S')
        original_df = pd.DataFrame(data,
                                   columns=['Obstructive'], index=tidx)

        result_df = generate_annotations(original_df, length_event='10S')

        assert (result_df['ApneaEvent'].isin([0, 1]).sum(axis=0) == len(result_df))
        assert (result_df['ApneaEvent'].to_list() == [0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0])
        assert (result_df['Obstructive'].to_list() == original_df['Obstructive'].to_list())

    def test_generate_annotation_entire_event_size_lower(self):
        np.random.seed(10)

        rows, cols = 5, 1
        data = [0, 0, 0, 23, 0]
        tidx = pd.date_range('2019-01-01', periods=rows, freq='S')
        original_df = pd.DataFrame(data,
                                   columns=['Obstructive'], index=tidx)

        result_df = generate_annotations(original_df, length_event='10S')

        assert (result_df['ApneaEvent'].isin([0, 1]).sum(axis=0) == len(result_df))
        assert (result_df['ApneaEvent'].to_list() == [1, 1, 1, 1, 0])
        assert (result_df['Obstructive'].to_list() == original_df['Obstructive'].to_list())

    def test_generate_annotation_multi_event(self):
        np.random.seed(10)

        rows, cols = 20, 2
        data = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 23, 0]
        data2 = [0, 0, 5, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        tidx = pd.date_range('2019-01-01', periods=rows, freq='S')
        original_df = pd.DataFrame(data,
                                   columns=['Obstructive'], index=tidx)
        original_df['ClearAirway'] = data2

        result_df = generate_annotations(original_df, length_event='10S')

        assert (result_df['ApneaEvent'].isin([0, 1]).sum(axis=0) == len(result_df))
        assert (result_df['ApneaEvent'].to_list() == [1, 1, 1, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0])
        assert (result_df['Obstructive'].to_list() == original_df['Obstructive'].to_list())
        assert (result_df['ClearAirway'].to_list() == original_df['ClearAirway'].to_list())

    def test_generate_annotation_multi_event_merge_some(self):
        np.random.seed(10)

        rows, cols = 20, 2
        data = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 23, 0]  # Obstructive
        data2 = [0, 0, 5, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]  # ClearAirway
        data3 = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0.5, 0, 0, 0, 0, 0, 0, 0, 0, 0]  # Hypopnea
        tidx = pd.date_range('2019-01-01', periods=rows, freq='S')
        original_df = pd.DataFrame(data,
                                   columns=['Obstructive'], index=tidx)
        original_df['ClearAirway'] = data2
        original_df['Hypopnea'] = data3

        result_df = generate_annotations(original_df,
                                         length_event='4S',
                                         output_events_merge=[ChannelID.CPAP_ClearAirway,
                                                              ChannelID.CPAP_Hypopnea])

        assert (result_df['ApneaEvent'].isin([0, 1]).sum(axis=0) == len(result_df))
        assert (result_df['ApneaEvent'].to_list() == [1, 1, 1, 0, 0, 0, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0])
        assert (result_df['Obstructive'].to_list() == original_df['Obstructive'].to_list())
        assert (result_df['ClearAirway'].to_list() == original_df['ClearAirway'].to_list())
        assert (result_df['Hypopnea'].to_list() == original_df['Hypopnea'].to_list())

