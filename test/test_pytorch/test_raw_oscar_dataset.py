import os
from unittest import TestCase

from src.pyapnea.pytorch.raw_oscar_dataset import RawOscarDataset
from src.pyapnea.utils.annotations import get_nb_events


class TestRawOscarDataset(TestCase):
    def test___getitem__(self):
        data_path = 'data/raw'
        ds = RawOscarDataset(data_path=data_path)

        assert len(ds) == 2
        # id elmnt, inputs, first timestep, first sensor
        assert ds[0][0][0][0] == 39.96000158786774
        # id elmnt, class
        assert ds[0][1][0] == 0

        nb_events, events = get_nb_events(ds)
        assert nb_events == 1
