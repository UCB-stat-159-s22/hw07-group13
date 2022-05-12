from aqtools import aqutils as u
import openaq
import numpy as np

def test_utc_to_pst():
    d = '2021-09-01T00:00:00Z'
    assert u.utc_to_pst(d) == '2021-08-31 17:00:00'


def test_pst_to_utc():
    d = '2021-09-01T00:00:00Z'
    assert u.pst_to_utc(d) == '2021-09-01 00:00:00'


def test_getaqi():
    no2_aqi = u.get_aqi('no2', 0.15)
    assert no2_aqi == 110


def test_cleaning_date_format():
    d = '2021-08-01T12:34:56Z'
    assert u.cleaning_date_format(d) == '2021-08-01 12:34:56'


def test_extract_localdate():
    d = [{'utc': '2020-03-01T00:00:00Z', 'local': '2022-03-06T12:34:56Z'}]
    assert u.extract_localdate(d)[0] == '2022-03-06 12:34:56'


def test_date_pollutant_value():
    api = openaq.OpenAQ()
    date_from = '2021-09-01T00:00:00Z'
    date_to = '2022-03-01T00:00:00Z'
    city = 'San Francisco-Oakland-Fremont'
    location = 'Oakland'
    data_query_limit = 100
    pollutant = 'co'
    status, resp = api.measurements(city=city,
                                location=location, parameter=pollutant,
                                date_from=date_from,
                                date_to=date_to,
                                limit=data_query_limit)
    r = resp['results']
    df_co = u.date_pollutant_value(r, pollutant)
    date_lst = df_co['date'].values
    assert any('2022-02-25 19:00:00' in date for date in date_lst)
