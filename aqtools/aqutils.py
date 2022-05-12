import pandas as pd
from datetime import datetime
import pytz

AQI_BREAKPOINTS = './data/aqi_breakpoints.csv'


def utc_to_pst(date_str):
    """Convert utc datetime to pst datetime

    :param date_str: string type datatime format

    :type data_str: string

    :returns: string format pst datetime
    """
    d = datetime.strptime(date_str, '%Y-%m-%dT%H:%M:%S%z').replace(minute=0)
    return d.astimezone(pytz.timezone('US/Pacific')).strftime('%Y-%m-%d %H:%M:%S')


def pst_to_utc(date_str):
    """Convert pst datetime to utc datetime

    :param date_str: string type datatime format

    :type data_str: string

    :returns: string format utc datetime
    """
    d = datetime.strptime(date_str, '%Y-%m-%dT%H:%M:%S%z').replace(minute=0)
    return d.astimezone(pytz.timezone('UTC')).strftime('%Y-%m-%d %H:%M:%S')


def get_aqi(pollutant, value):
    """Get AQI corresponding pollutant and value

    :param pollutant: type of pollutant
    :param value: value of pollutant

    :type endpoint: string
    :type method: float
    :returns: integer value of AQI
    """
    pollutants = {'pm25': 88502,
                  'co': 42101,
                  'no2': 42602,
                  'o3': 44201,
                  'pm10': 81102,
                  'so2': 42401}

    p = pollutants[pollutant]
    df = pd.read_csv(AQI_BREAKPOINTS)
    p_df = df[df['Parameter Code'] == p]
    aqi = p_df[(p_df['Low Breakpoint'] <= value) & (value < p_df['High Breakpoint'])]
    Cp = value
    BPHi = aqi['High Breakpoint'].values[0]
    BPLo = aqi['Low Breakpoint'].values[0]
    IHi = aqi['High AQI'].values[0]
    ILo = aqi['Low AQI'].values[0]
    IP = (IHi - ILo)/(BPHi - BPLo) * (Cp - BPLo) + ILo
    return int(IP)


def cleaning_date_format(s):
    """Cleaning dateformat
    :param s: date format e.g. '2021-08-01T00:00:00Z'

    :type s: string

    :returns: a string of clean format of date e.g. '2021-08-01 00:00:00'
    """
    ymd = s.split('T')[0]
    hms = s.split('T')[1][:-1]
    return ymd + ' ' + hms


def extract_localdate(dates):
    """Extracting local date from [{'utc': 'YY-mm-ddT00:00:00Z', 'local': 'YY-mm-ddT00:00:00Z'}]

    :param dates: list of dictionaries containing keys('utc', 'local') and corresponding date values

    :type dates: list, numpy array

    :returns: list of local dates e.g. ['2020-01-02T12:34:56Z', '2022-01-02T12:34:56Z']
    """
    local_dates = []
    for d in dates:
        local_date = d['local']
        local_date_clean = cleaning_date_format(local_date)
        local_dates.append(local_date_clean)
    return local_dates


def date_pollutant_value(lst_of_dict, pollutant):
    """Take openaq results and Transform data into dataframe with date, pollutant type, value

    :param lst_of_dict: results from openaq.
    :param pollutant: type of pollutant

    :type lst_of_dict: list type
    :type pollutant: string

    :return: dataframe with date, type of pollutant and value columns
    """
    df = pd.DataFrame(data=lst_of_dict)
    df['date'] = extract_localdate(df['date'].values)
    df['date'] = pd.to_datetime(df['date'])
    df = df.rename(columns={"value": pollutant})
    df = df.loc[:, ['date', pollutant]]
    df = df.iloc[::-1]
    df = df[df[pollutant] >= 0]
    return df


def differencing(arr):
    """Differencing for stationarity

    :param arr: list type string sequences

    :type arr: list, numpy array

    :returns: list of stationary data
    """
    diff_lst = []
    for i, v in enumerate(arr):
        if i == 0:
            continue
        diff = v - arr[i-1]
        diff_lst.append(diff)
    return diff_lst
