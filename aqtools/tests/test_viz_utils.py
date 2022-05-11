from aqtools import viz_utils as vu
import openaq
import pandas as pd
import geopandas as gpd
import os
import pytest

api = openaq.OpenAQ()
pytest.shared = pd.DataFrame()

def test_location_filter():
    df = vu.location_filter(api.locations(country='US', df=True, limit=10000))
    assert df.size == 1173
    pytest.shared1 = df


def test_param_data_per_loc_for_period():
    df = vu.param_data_per_loc_for_period(pytest.shared1, start_date= '2020-09-07', end_date='2020-09-13', param='pm25', limit=1000, interpolate=True)
    assert df.size == 6348
    pytest.shared2 = df

def test_cities_coords():
    geodata, list_type = vu.cities_coords(pytest.shared1, pytest.shared2)
    assert (geodata.shape == (46, 2)) and (len(list_type) == 55)
    pytest.shared3 = geodata
    pytest.shared4 = list_type

def test_merge_and_save_gdf():
    bay_data = vu.merge_and_save_gdf(pytest.shared3, pytest.shared2, save=False, filename='data/bayareadarkdays.geojson')
    assert bay_data.shape == (46, 139)
    pytest.shared5 = bay_data

def test_pointmap_compare():
    world = gpd.read_file("https://data.sfgov.org/api/geospatial/s9wg-vcph?method=export&format=Shapefile")
    bay_data = gpd.read_file('data/bayareadarkdays.geojson')
    vu.pointmap_compare(loc_name='Bay Area', param='pm25',data = bay_data, date1='2020-09-06 17:00:00', date2='2020-09-06 19:00:00', basemap=world, center_lat=37.8711428, center_lon=-122.3714777,
                 color_min=0, color_max=342, xmin=-50000,xmax=60000, ymin=-60000, ymax=50000, min_scale=50, max_scale=50, save=True, save_loc='figures/testing_temp_figs/')
    assert sum([File.endswith(".png") for File in os.listdir("figures/testing_temp_figs")]) == 1
    test = os.listdir('figures/testing_temp_figs')
    for item in test:
        if item.endswith(".png"):
            os.remove(os.path.join('figures/testing_temp_figs', item))

def test_pointmap_single():
    world = gpd.read_file("https://data.sfgov.org/api/geospatial/s9wg-vcph?method=export&format=Shapefile")
    bay_data = gpd.read_file('data/bayareadarkdays.geojson')
    vu.pointmap_single(loc_name='Bay Area', param='pm25',data = bay_data, date1='2020-09-06 17:00:00', basemap=world, center_lat=37.8711428, center_lon=-122.3714777,
                 color_min=0, color_max=342, xmin=-50000,xmax=60000, ymin=-60000, ymax=50000, min_scale=50, max_scale=50, save=True,save_loc='figures/testing_temp_figs/')
    assert sum([File.endswith(".png") for File in os.listdir("figures/testing_temp_figs")]) == 1
    test = os.listdir('figures/testing_temp_figs')
    for item in test:
        if item.endswith(".png"):
            os.remove(os.path.join('figures/testing_temp_figs', item))

def test_aqviz():
    bay_data = gpd.read_file('data/bayareadarkdays.geojson')
    vu.aqviz(bay_data, pytest.shared4, '2020-09-06 17:00:00', 'pm25', save=True, save_loc='figures/testing_temp_figs/')
    assert sum([File.endswith(".png") for File in os.listdir("figures/testing_temp_figs")]) == 1
    test = os.listdir('figures/testing_temp_figs')
    for item in test:
        if item.endswith(".png"):
            os.remove(os.path.join('figures/testing_temp_figs', item))