Tutorial
========

PyApnea is able to read .001 files from Oscar Data structure. In this tutorial, we'll see how to read a file from this structure and how to transform it to a dataframe.

Loading a .001 file into a dataframe
-------------------------------

Assuming you have a file named '61f5f33c.001'. This file can be found in the `test/` directory of PyApnea source code.

    from pyapnea.oscar.oscar_loader import load_session
    from pyapnea.oscar.oscar_getter import event_data_to_dataframe
    from pyapnea.oscar.oscar_constants import ChannelID

    # this will read the file and transform it to an internal data structure (see data_structure.py)
    oscar_session_data = load_session('61f5f33c.001')

    # this line takes an internal data structure and transform it into a pandas dataframe
    df = event_data_to_dataframe(oscar_session_data=oscar_session_data,
                                 channel_ids=[ChannelID.CPAP_FlowRate.value])

The result should be the following :

                                   time_utc   FlowRate
    0             2022-01-30 02:09:19+00:00  39.960002
    1      2022-01-30 02:09:19.040000+00:00  38.640002
    2      2022-01-30 02:09:19.080000+00:00  38.160002
    3      2022-01-30 02:09:19.120000+00:00  36.840001
    4      2022-01-30 02:09:19.160000+00:00  34.200001
    ...                                 ...        ...
    361495 2022-01-30 06:35:21.800000+00:00  18.720001
    361496 2022-01-30 06:35:21.840000+00:00  18.600001
    361497 2022-01-30 06:35:21.880000+00:00  18.000001
    361498 2022-01-30 06:35:21.920000+00:00  17.160001
    361499 2022-01-30 06:35:21.960000+00:00  15.600001
    
    [397500 rows x 2 columns]
             
Note that the column `time_utc`, as its name suggests, is the UTC time of the points. You can load multiple channels into the dataframe. 

    df = event_data_to_dataframe(oscar_session_data=oscar_session_data,
                                 channel_ids=[ChannelID.CPAP_FlowRate.value,
                                              ChannelID.CPAP_Obstructive.value,
                                              ChannelID.CPAP_ClearAirway.value])

And the result :

                                   time_utc   FlowRate  Obstructive  ClearAirway
    0             2022-01-30 02:09:19+00:00  39.960002          NaN          NaN
    1      2022-01-30 02:09:19.040000+00:00  38.640002          NaN          NaN
    2      2022-01-30 02:09:19.080000+00:00  38.160002          NaN          NaN
    3      2022-01-30 02:09:19.120000+00:00  36.840001          NaN          NaN
    4      2022-01-30 02:09:19.160000+00:00  34.200001          NaN          NaN
    ...                                 ...        ...          ...          ...
    397496 2022-01-30 06:35:21.840000+00:00  18.600001          NaN          NaN
    397497 2022-01-30 06:35:21.880000+00:00  18.000001          NaN          NaN
    397498 2022-01-30 06:35:21.920000+00:00  17.160001          NaN          NaN
    397499 2022-01-30 06:35:21.960000+00:00  15.600001          NaN          NaN
    397500        2022-01-30 02:33:23+00:00        NaN          NaN         10.0


    [397500 rows x 3 columns]

Some remarks can be made from this result. First, the channel `CPAP_Obstructive` is present in the file but does not have any value. Secondly, the `CPAP_ClearAirway` contains values, but they are not in a logical order. Ths dataframe needs to have a sorted index :

    df.set_index('time_utc', inplace=True)
    df.sort_index(inplace=True)
    print(df)

With the result :

                                       FlowRate  Obstructive  ClearAirway
    time_utc                                                             
    2022-01-30 02:09:19+00:00         39.960002          NaN          NaN
    2022-01-30 02:09:19.040000+00:00  38.640002          NaN          NaN
    2022-01-30 02:09:19.080000+00:00  38.160002          NaN          NaN
    2022-01-30 02:09:19.120000+00:00  36.840001          NaN          NaN
    2022-01-30 02:09:19.160000+00:00  34.200001          NaN          NaN
    ...                                     ...          ...          ...
    2022-01-30 06:35:21.800000+00:00  18.720001          NaN          NaN
    2022-01-30 06:35:21.840000+00:00  18.600001          NaN          NaN
    2022-01-30 06:35:21.880000+00:00  18.000001          NaN          NaN
    2022-01-30 06:35:21.920000+00:00  17.160001          NaN          NaN
    2022-01-30 06:35:21.960000+00:00  15.600001          NaN          NaN

You can find value of the `CPAP_ClearAirway` by searching into the dataframe :

    print(df[df.ClearAirway.notnull()])

And the result (some ClearAirway, this night !):

                              FlowRate  Obstructive  ClearAirway
    time_utc                                                     
    2022-01-30 02:33:23+00:00       NaN          NaN         10.0
    2022-01-30 03:06:37+00:00      0.48          NaN         16.0
    2022-01-30 03:25:50+00:00      1.20          NaN         11.0
    2022-01-30 03:28:10+00:00      9.36          NaN         12.0
    2022-01-30 04:49:34+00:00    -10.08          NaN         15.0
    2022-01-30 05:02:07+00:00      3.36          NaN         21.0
    2022-01-30 05:16:17+00:00      4.44          NaN         14.0
    2022-01-30 06:21:43+00:00     -0.96          NaN         15.0
    2022-01-30 06:31:29+00:00      1.92          NaN         13.0

Do not forget that the result of `event_data_to_dataframe()` is a pandas dataframe, so any dataframe
operation is accessible to organize data.

RawOscarDataset
---------------

Soon...

ProcessedDataset
----------------

Soon...


