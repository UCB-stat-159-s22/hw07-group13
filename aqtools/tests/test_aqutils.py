from aqtools import aqutils as u


def test_getaqi():
    no2_aqi = u.get_aqi('no2', 0.15)
    assert no2_aqi == 110
