import pandas as pd
from geopandas import GeoDataFrame
import geoplot as gplt
import geoplot.crs as gcrs
import numpy as np
import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)
import openaq
from shapely.geometry import Point
import matplotlib as mpl
import matplotlib.pyplot as plt


from scipy.interpolate import griddata
from mpl_toolkits.basemap import Basemap
from matplotlib.colors import Normalize



def location_filter(orig_table, minlat = 36., minlon = -123.5, maxlat=39., maxlon = -121, starttime='2020-09-07', endtime='2020-09-13'):
    
    '''
    inputs:
        orig_table: the result of an api.location() call; e.g. the US locs
    
    
    output:
        filtered_table: a DataFrame containing the original locations that pass the lat-lon and date filters
    
    
    '''
    
    filter1 = orig_table[orig_table['coordinates.latitude'] > minlat]
    filter2= filter1[filter1['coordinates.latitude'] < maxlat]
    filter3 = filter2[filter2['coordinates.longitude'] < maxlon]
    filter4 = filter3[filter3['coordinates.longitude'] > minlon]
    filter5 = filter4[filter4['firstUpdated'] < starttime + ' 00:00:00+00:00']
    filtered_table = filter5[filter5['lastUpdated'] > endtime +  ' 00:00:00+00:00']
    return filtered_table



def param_data_per_loc_for_period(loc_table, start_date= '2020-09-07', end_date='2020-09-13', param='pm25', limit=1000, interpolate=True):
    
    '''
    input:
        loc_table: result from filtered table
    
    output:
        df: a DataFrame of each location's data for the parameter specified for the date range specified.
            Results will be forwards and backwards interpolated in interpolate=True
   
    '''
    
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
            if location in dark_days_data:
                location = str(location) +'_'+ str(np.random.randint(0,1000000))
            dark_days_data[location] = list()
            dark_days_data[location].append(coords)
            dark_days_data[location].append(date_vals)

        except KeyError:
            continue
        except:
            raise

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
    inputs:
        loc_table is a dataframe that is the output of location_filter
        df is a dataframe that is the output of param_data_per_loc_for_period
    
    outputs:
        cities_coords: a GeoDataFrame of cities coordinates
        coord_list: a list of all of the coordinates, to be used in the aqviz() plotter function 
    
    '''
    name_list = []
    coord_list = []
    for (columnName, columnData) in df.iteritems():
        for index, row in loc_table.iterrows():
            if row['location'] in columnName:
                name_list.append(columnName)
                coord_list.append((row['coordinates.longitude'], row['coordinates.latitude']))
         
    geometry = [Point(xy) for xy in coord_list]
    cities_coords = GeoDataFrame(name_list, geometry=geometry)
    cities_coords = cities_coords.drop_duplicates(subset=[0])
    return cities_coords, coord_list

def merge_and_save_gdf(cities_coords, data, save=True, filename='data/bayareadarkdays.geojson'):
    '''
    inputs:
        cities_coords: is the first result of the cities_coords() function
        data: is the result of param_data_per_loc_for_period()
    
    returns:
        temp, a full Dataframe containing all data in a merged format that can be read by the plotting functions.
            if save=True, saves temp as a GeoJSON file in the filename location   
    
    
    '''
    
    temp = cities_coords.set_index([0])
    for i in range(data.shape[0]):
        dftemp =  pd.DataFrame(data.iloc[i])
        temp = pd.concat([temp, dftemp], axis=1)
    if save:
        temp_text = temp
        temp_text.columns = temp_text.columns.astype(str)
        temp_text.to_file(filename, driver='GeoJSON')  
    return temp

def pointmap_compare(data, basemap, loc_name='Bay Area', param='pm25', date1='2020-09-06 17:00:00', date2='2020-09-06 19:00:00', center_lat=37.8711428, center_lon=-122.3714777,
                 color_min=0, color_max=342, xmin=-50000,xmax=60000, ymin=-60000, ymax=50000, min_scale=50, max_scale=50, save=True, save_loc='figures/'):
    
    '''
    Creates two geoplot point plots comparing param value on date1 and date2   
    
    input: 
        data: the result of the merge_and_save_gdf() file
        basemap: variable pointing to a basemap to go under the pointmap
        
     output:
         fig: the two geoplots
         
    
    
    
    '''
    
    norm = mpl.colors.Normalize(vmin=color_min, vmax=color_max)
    cmap = mpl.cm.ScalarMappable(norm=norm, cmap='inferno_r').cmap

    proj = gcrs.AlbersEqualArea(central_latitude=center_lat, central_longitude=center_lon)
    fig= plt.figure(figsize=(20, 10))
    ax1 = plt.subplot(121, projection=proj)
    ax2 = plt.subplot(122, projection=proj)

    gplt.pointplot(data, projection=proj, hue=date1, legend=False,scale=date1, limits=(min_scale, max_scale), cmap=cmap, norm=norm, ax=ax1)
    gplt.polyplot(basemap, zorder=1, ax=ax1)
    ax1.axis(xmin=xmin,xmax=xmax, ymin=ymin, ymax=ymax)
    ax1.set_title(loc_name + ' '+ param + " on "+ str(date1))
    ax1_cbar = fig.colorbar(mpl.cm.ScalarMappable(norm=norm, cmap=cmap), ax=ax1)
    ax1_cbar.set_label(param)

    gplt.pointplot(data, projection=proj, hue=date2, legend=False,scale=date2, limits=(min_scale, max_scale), cmap=cmap, norm=norm, ax=ax2)
    gplt.polyplot(basemap, zorder=1, ax=ax2)
    ax2.axis(xmin=xmin,xmax=xmax, ymin=ymin, ymax=ymax)
    ax2.set_title(loc_name + ' '+ param + " on " + str(date2))
    ax2_cbar = fig.colorbar(mpl.cm.ScalarMappable(norm=norm, cmap=cmap), ax=ax2)
    ax2_cbar.set_label(param)
    if save:
        plt.savefig(save_loc+loc_name.replace(" ", "_") + '_'+ param + "_"+ str(date1).replace(" ", "_")+'_'+ str(date2).replace(" ", "_")+'.png')
        
    return fig

    
def pointmap_single(data, basemap, loc_name='Bay Area', param='pm25', date1='2020-09-06 17:00:00', center_lat=37.8711428, center_lon=-122.3714777,
                 color_min=0, color_max=342, xmin=-50000,xmax=60000, ymin=-60000, ymax=50000, min_scale=50, max_scale=50, save=True,save_loc='figures/'):
    
    '''
    Creates a single geoplot point plot of one param value on date1  
    
    input: 
        data: the result of the merge_and_save_gdf() file
        basemap: variable pointing to a basemap to go under the pointmap
        
     output:
         fig: the two geoplots
         
    
    
    
    '''
    
    norm = mpl.colors.Normalize(vmin=color_min, vmax=color_max)
    cmap = mpl.cm.ScalarMappable(norm=norm, cmap='inferno_r').cmap

    proj = gcrs.AlbersEqualArea(central_latitude=center_lat, central_longitude=center_lon)
    fig= plt.figure(figsize=(10, 10))
    ax1 = plt.subplot(111, projection=proj)


    gplt.pointplot(data, projection=proj, hue=date1, legend=False,scale=date1, limits=(min_scale, max_scale), cmap=cmap, norm=norm, ax=ax1)
    gplt.polyplot(basemap, zorder=1, ax=ax1)
    ax1.axis(xmin=xmin,xmax=xmax, ymin=ymin, ymax=ymax)
    ax1.set_title(loc_name + ' '+ param + " on "+ str(date1))
    ax1_cbar = fig.colorbar(mpl.cm.ScalarMappable(norm=norm, cmap=cmap), ax=ax1)
    ax1_cbar.set_label(param)
    if save:
        plt.savefig(save_loc+loc_name.replace(" ", "_") + '_'+ param + "_"+ str(date1).replace(" ", "_")+'.png')
    return fig

def aqviz(dataframe, coords, date='2020-09-06 17:00:00', param='pm25', save=True, save_loc='figures/'):
    
    '''
    Based on: https://stackoverflow.com/questions/26872337/how-can-i-get-my-contour-plot-superimposed-on-a-basemap
    
    Creates a heatmap based on param values for a specific date
    
    inputs:
        dataframe: the result from the merge_and_save_gdf() function
        coords: coordinates of the locations, second result from cities_coords() function

    outputs:
        a figure of the heatmap
    
    
    '''
    
    
    # set up plot
    plt.clf()
    fig = plt.figure(figsize=(10, 10))
    ax = fig.add_subplot(111, frame_on=False)

    # grab data
    lats = []
    lons = []
    for i in range(len(coords)):
        lats.append(coords[i][1])
        lons.append(coords[i][0])
    
    data= pd.DataFrame()
    data['Lat'] = lats
    data['Lon'] = lons
    
    data['Z'] = dataframe[date]

    norm = Normalize()

    # define map extent
    lllon = min(data.Lon.values)
    lllat = min(data.Lat.values)
    urlon = max(data.Lon.values)
    urlat = max(data.Lat.values)


    # Set up Basemap instance
    m = Basemap(
        projection = 'merc',
        llcrnrlon = lllon, llcrnrlat = lllat, urcrnrlon = urlon, urcrnrlat = urlat,
        resolution='i')

    # transform lon / lat coordinates to map projection
    data['projected_lon'], data['projected_lat'] = m(*(data.Lon.values, data.Lat.values))

    # # grid data
    numcols, numrows = 1000, 1000
    xi = np.linspace(data['projected_lon'].min(), data['projected_lon'].max(), numcols)
    yi = np.linspace(data['projected_lat'].min(), data['projected_lat'].max(), numrows)
    xi, yi = np.meshgrid(xi, yi)

    # # interpolate
    x, y, z = data['projected_lon'].values, data['projected_lat'].values, data.Z.values
    zi = griddata((x, y), z, (xi, yi))

    # # draw map details
    m.drawmapboundary(fill_color = 'white')
    m.fillcontinents(color='#C0C0C0', lake_color='#7093DB')
    m.drawcountries(
        linewidth=.75, linestyle='solid', color='#000073',
        antialiased=True,
        ax=ax, zorder=3)
    m.drawcoastlines()


    # # contour plot
    con = m.pcolormesh(xi, yi, zi, zorder=20, alpha=0.6, cmap='inferno_r', vmin=0, vmax=341)
    # scatter plot
    m.scatter(
        data['projected_lon'],
        data['projected_lat'],
        color='#545454',
        edgecolor='#ffffff',
        alpha=.75,
        ax=ax,
        vmin=zi.min(), vmax=zi.max(), zorder=20)

    # # add colour bar and title
    # # add colour bar, title, and scale
    cbar = plt.colorbar(orientation='vertical', fraction=.057, pad=0.05)
    cbar.set_label(param)
    plt.title("Bay Area AQ -- " + param + " " + str(date))
    if save:
        plt.savefig(save_loc+'Bay_Area_AQ_'+ param + "_"+ str(date).replace(" ", "_")+'.png')
