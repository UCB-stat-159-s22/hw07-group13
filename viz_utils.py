import pandas as pd
from geopandas import GeoDataFrame
import numpy as np
import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)
import openaq
from shapely.geometry import Point


def location_filter(orig_table, minlat = 36., minlon = -123.5, maxlat=39., maxlon = -121, starttime='2020-09-07', endtime='2020-09-13'):
    filter1 = orig_table[orig_table['coordinates.latitude'] > minlat]
    filter2= filter1[filter1['coordinates.latitude'] < maxlat]
    filter3 = filter2[filter2['coordinates.longitude'] < maxlon]
    filter4 = filter3[filter3['coordinates.longitude'] > minlon]
    filter5 = filter4[filter4['firstUpdated'] < starttime + ' 00:00:00+00:00']
    filtered_table = filter5[filter5['lastUpdated'] > endtime +  ' 00:00:00+00:00']
    return filtered_table



def param_data_per_loc_for_period(loc_table, start_date= '2020-09-07', end_date='2020-09-13', param='pm25', limit=1000, interpolate=True):
    api = openaq.OpenAQ()
    city_list = loc_table.reset_index()
    dark_days_data = {}
    for index, row in city_list.iterrows():
        location = row['location']
        coords = (row['coordinates.longitude'], row['coordinates.latitude'])
        if row['parameters'].count(param) == 0:
            continue
        try:
            table = api.measurements(location=location, parameter=param, 
                                 date_from= start_date, date_to=end_date, df=True, limit=limit)
            table = table.reset_index()
            date_vals = dict(list(zip(table['date.local'], table['value'])))
            if dark_days_data.has_key(location):
                location = location +'_'+ str(np.random.randint(0,1000000))
            dark_days_data[location] = list()
            dark_days_data[location].append(coords)
            dark_days_data[location].append(date_vals)
        except:
            continue
    df = pd.DataFrame.from_dict(dark_days_data[list(dark_days_data.keys())[0]][1], orient='index', columns=[list(dark_days_data.keys())[0]])
    for key in dark_days_data.keys():
        df2 = pd.DataFrame.from_dict(dark_days_data[key][1], orient='index', columns=[key])
        df = pd.concat([df, df2], axis=1)
    df = df.loc[:,~df.columns.duplicated()]
    if interpolate:
        df = df.interpolate(method='linear', limit_direction='forward', axis=0)
        df = df.interpolate(method='linear', limit_direction='backward', axis=0)
    return df


def cities_coords(loc_table, df):
    ''' 
    loc_table is a dataframe that is the output of location_filter
    df is a dataframe that is the output of param_data_per_loc_for_period
    
    '''
    
    name_list = []
    coord_list = []
    for index, row in loc_table.iterrows():
        name_list.append(row['location'])
        coord_list.append((row['coordinates.longitude'], row['coordinates.latitude']))
    geometry = [Point(xy) for xy in coord_list]
    cities_coords = GeoDataFrame(name_list, geometry=geometry)
    cities_coords = cities_coords[cities_coords[0].isin(df.columns)]
    return cities_coords