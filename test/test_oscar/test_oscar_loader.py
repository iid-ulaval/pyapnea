from unittest import TestCase
from datetime import datetime, timezone

from dataclasses import asdict
from src.pyapnea.oscar.oscar_loader import read_session, load_session
from src.pyapnea.oscar.oscar_getter import get_channel_from_code, event_data_to_dataframe
from src.pyapnea.oscar.oscar_constants import ChannelID

expected_oscar_data_dict = {'header': {'magicnumber': 3341948587,
                                       'version': 10,
                                       'filetype': 1,
                                       'deviceid': 2327,
                                       'sessionid': 1673980200,
                                       'sfirst': 1673980203000,
                                       'slast': 1673981224000,
                                       'compmethod': 0,
                                       'machtype': 1,
                                       'datasize': 114270,
                                       'crc16': 0},
                            'data': {'mcsize': 17,
                                     'channels': [{'code': 4362,
                                                   'size2': 1,
                                                   'events': [{'ts1': 1673980205440,
                                                               'ts2': 1673981218560,
                                                               'evcount': 327,
                                                               't8': 1,
                                                               'rate': 0.0,
                                                               'gain': 0.019999999552965164,
                                                               'offset': 0.0,
                                                               'mn': 0.47999998927116394,
                                                               'mx': 2.4600000381469727,
                                                               'len_dim': -1,
                                                               'dim': "",
                                                               'second_field': False,
                                                               'mn2': 0.0,
                                                               'mx2': 0.0,
                                                               'data': [26, 58, 71, 97, 93, 100, 93, 98, 94, 90, 85, 81,
                                                                        78, 75, 82, 81, 87, 83, 79, 84, 87, 89, 93, 93,
                                                                        95, 92, 102, 109, 116, 104, 100, 94, 98, 95, 96,
                                                                        96, 94, 94, 94, 93, 97, 92, 88, 84, 89, 88, 90,
                                                                        92, 94, 97, 96, 88, 80, 80, 84, 93, 91, 92, 85,
                                                                        86, 84, 84, 89, 92, 87, 86, 83, 90, 84, 83, 80,
                                                                        85, 87, 87, 94, 55, 30, 24, 43, 44, 69, 88, 97,
                                                                        98, 89, 83, 87, 91, 104, 100, 103, 100, 100,
                                                                        101, 102, 95, 85, 73, 88, 89, 92, 90, 93, 84,
                                                                        88, 87, 92, 93, 92, 94, 88, 89, 96, 88, 96, 95,
                                                                        95, 97, 95, 95, 97, 95, 92, 89, 87, 89, 90, 98,
                                                                        88, 96, 92, 100, 104, 94, 91, 84, 87, 83, 85,
                                                                        82, 94, 87, 92, 91, 88, 87, 82, 91, 93, 96, 96,
                                                                        100, 103, 99, 92, 87, 87, 85, 92, 87, 84, 81,
                                                                        56, 55, 66, 86, 98, 96, 120, 73, 93, 83, 96, 99,
                                                                        105, 114, 111, 96, 102, 107, 98, 98, 92, 97, 86,
                                                                        95, 107, 116, 106, 104, 84, 80, 84, 95, 90, 94,
                                                                        107, 101, 103, 98, 92, 97, 77, 82, 78, 88, 100,
                                                                        102, 100, 103, 100, 106, 104, 101, 102, 87, 93,
                                                                        93, 94, 102, 101, 102, 102, 95, 73, 86, 83, 87,
                                                                        98, 99, 101, 100, 97, 100, 97, 95, 97, 110, 109,
                                                                        94, 91, 78, 85, 89, 84, 88, 93, 97, 106, 106,
                                                                        57, 46, 56, 81, 107, 93, 86, 83, 102, 111, 123,
                                                                        113, 99, 93, 87, 88, 92, 103, 101, 96, 79, 69,
                                                                        76, 85, 104, 101, 95, 101, 104, 101, 104, 104,
                                                                        109, 103, 106, 103, 107, 100, 101, 97, 98, 91,
                                                                        95, 103, 106, 104, 98, 53, 48, 25, 45, 58, 62,
                                                                        57, 53, 64, 80, 99, 99, 107, 86, 97, 107, 104,
                                                                        122, 111, 94, 100, 98, 95, 83, 99, 92, 90, 81,
                                                                        78, 87],
                                                               'data2': [],
                                                               'time': [0, 3120, 6560, 9480, 13280, 16600, 20000, 23400,
                                                                        26800, 29920, 33120, 35760, 38560, 41280, 44520,
                                                                        47520, 50360, 53240, 56120, 58800, 61960, 65000,
                                                                        68040, 71320, 74480, 77840, 81080, 84840, 88880,
                                                                        92440, 95360, 98800, 102080, 105400, 108680,
                                                                        111880, 115200, 118440, 121520, 124840, 127840,
                                                                        131320, 134280, 137160, 140160, 143360, 146480,
                                                                        149600, 152760, 156080, 159360, 162560, 165360,
                                                                        168040, 171000, 174280, 177560, 180480, 183480,
                                                                        186360, 189320, 192360, 195360, 198560, 201640,
                                                                        204400, 207280, 210160, 213440, 216120, 218880,
                                                                        221720, 224760, 227880, 230920, 233760, 235120,
                                                                        235920, 237600, 239520, 241400, 244440, 247920,
                                                                        250960, 253960, 256960, 259480, 262560, 265640,
                                                                        269080, 272440, 275920, 279080, 282080, 285320,
                                                                        288560, 291520, 294080, 296520, 299920, 303240,
                                                                        306160, 309080, 312280, 315120, 318160, 321160,
                                                                        324240, 327360, 330440, 333720, 336520, 339560,
                                                                        342840, 345600, 348760, 352480, 355480, 358640,
                                                                        361800, 365000, 368200, 371360, 374280, 377280,
                                                                        380360, 383440, 386360, 389600, 392400, 395720,
                                                                        399000, 402360, 405880, 408800, 411880, 414800,
                                                                        417840, 420640, 423600, 426520, 429800, 432480,
                                                                        435600, 438880, 441800, 444640, 447480, 450720,
                                                                        453960, 457040, 460280, 463680, 467200, 470200,
                                                                        473040, 476000, 478960, 481840, 485040, 487880,
                                                                        490880, 493760, 495040, 497160, 500080, 503400,
                                                                        506600, 509680, 514280, 514960, 518080, 521160,
                                                                        524120, 527280, 530720, 534360, 538160, 541000,
                                                                        544640, 548360, 551320, 554720, 557960, 561360,
                                                                        564240, 567640, 571520, 575240, 578400, 581800,
                                                                        584480, 587240, 590560, 594000, 596880, 600200,
                                                                        604320, 607480, 610960, 614200, 617120, 620640,
                                                                        623000, 625840, 628880, 632040, 635760, 639120,
                                                                        642360, 645960, 649280, 653240, 656680, 660040,
                                                                        663480, 666160, 669680, 673320, 676600, 680200,
                                                                        683480, 686800, 690040, 692840, 695080, 698440,
                                                                        701520, 704400, 708160, 711720, 715080, 718640,
                                                                        722160, 725640, 729000, 732480, 735560, 739440,
                                                                        743240, 746240, 749600, 752560, 755720, 759360,
                                                                        762440, 765880, 769360, 773240, 776960, 780320,
                                                                        781040, 781880, 784880, 787960, 791920, 794600,
                                                                        797280, 801480, 805200, 808800, 813040, 816520,
                                                                        819400, 822720, 825840, 829440, 832840, 836440,
                                                                        839840, 843040, 845760, 848120, 851040, 854520,
                                                                        858120, 861360, 864360, 868080, 871560, 874840,
                                                                        878400, 882000, 885720, 889960, 893680, 897120,
                                                                        900640, 903800, 907120, 910280, 913600, 916840,
                                                                        920280, 923920, 927400, 930640, 933760, 934360,
                                                                        935880, 936880, 938920, 941600, 943720, 945240,
                                                                        946880, 949360, 952360, 955960, 958960, 962240,
                                                                        964800, 968240, 972000, 975320, 979400, 982680,
                                                                        985400, 989000, 992720, 995280, 998160, 1002120,
                                                                        1005000, 1007760, 1010400, 1013120]}]
                                                   }
                                                  ]
                                     }
                            }


def find_value_in(element, tv_dict):
    keys = element.split('/')
    keys = keys[1:]
    rv = tv_dict
    for key in keys:
        if rv is not None and type(rv) is dict and key in rv:
            rv = rv[key]
        else:
            rv = None
    return rv


class TestOscarSessionLoader(TestCase):

    def _test(self, oscar_session_data):
        self.maxDiff = None

        # remove some element to oscar_session_data to get only some elements to compare
        oscar_session_data.data.channels = [oscar_session_data.data.channels[0]]
        oscar_session_data.data.channels[0].events = [oscar_session_data.data.channels[0].events[0]]
        oscar_session_data_dict = asdict(oscar_session_data)

        self.assertDictEqual(expected_oscar_data_dict, oscar_session_data_dict)

    def test_read_session(self):
        filename = '../data/63c6e928.001'
        with open(filename, mode='rb') as file:  # b is important -> binary
            data = file.read()
            position = 0
            position, oscar_session_data = read_session(data, position)
            self._test(oscar_session_data)

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


