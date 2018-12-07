import numpy as np
import xarray as xr
import datetime as dt

import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cfeature

def snow_depth(lon, lat, month):
    """
    Calculates Warren snow depth climatology for an array of latitude and
    and longitude points for a given month.  Parameters are from Table 1
    of Warren, S.G., I.G. Rigor, and N. Untersteiner. 1999. Snow Depth on
    Arctic Sea Ice. J. Climate, 12, 1814 1829, 
    https://doi.org/10.1175/1520-0442(1999)012<1814:SDOASI>2.0.CO;2  

    Arguments
    ---------
    lon - array of latitude points (must be same size as lat)
    lat - array of longitude points (must be same size as lon)
    month - month number (1 to 12)

    Returns
    -------
    Numpy array of snow depths in cm with same shape as lon

    To Do
    -----
    Do I need to have parameters as numpy arrays.
    Need to make sure lon and lat are numpy arrays
    """

    im = month - 1

    h0 = np.array( [28.01,   30.28,   33.89,   36.80,   36.93,   36.59,
                    11.02,    4.64,   15.81,   22.66,   25.57,   26.67] )
    a  = np.array( [ 0.1270,  0.1056,  0.5486,  0.4046,  0.0214,  0.7021,
                     0.3008,  0.3100,  0.2119,  0.3594,  0.1496, -0.1876] )
    b  = np.array( [-1.1833, -0.5908, -0.1996, -0.4005, -1.1795, -1.4819,
                    -1.2591, -0.6350, -1.0292, -1.3483, -1.4643, -1.4229] )
    c  = np.array( [-0.1164, -0.0263,  0.0280,  0.0256, -0.1076, -0.1195,
                    -0.0811, -0.0655, -0.0868, -0.1063, -0.1409, -0.1413] )
    d  = np.array( [-0.0051, -0.0049,  0.0216,  0.0024, -0.0244, -0.0009,
                    -0.0043,  0.0059, -0.0177,  0.0051, -0.0079, -0.0316] )
    e  = np.array( [ 0.0243,  0.0044, -0.0176, -0.0641, -0.0142, -0.0603,
                     -0.0959, -0.0005, -0.0723, -0.0577, -0.0258, -0.0029] )

    x = (90. - lat) * np.cos( np.radians(lon) )
    y = (90. - lat) * np.sin( np.radians(lon) )

    h = ( h0[im] + ( a[im] * x ) + ( b[im] * y ) + ( c[im] * x * y ) +
          ( d[im] * x * x ) + ( e[im] * y * y ) )

    return h

def swe(lon, lat, month):
    """
    Calculates Warren swe climatology for an array of latitude and
    and longitude points for a given month.  Parameters are from
    table 2 of Warren, S.G., I.G. Rigor, and N. Untersteiner. 1999. Snow Depth on
    Arctic Sea Ice. J. Climate, 12, 1814 1829, 
    https://doi.org/10.1175/1520-0442(1999)012<1814:SDOASI>2.0.CO;2  

    Arguments
    ---------
    lon - array of latitude points (must be same size as lat)
    lat - array of longitude points (must be same size as lon)
    month - month number (1 to 12)

    Returns
    -------
    Numpy array of snow water equivalent in cm with same shape as lon
    """

    im = month - 1

    h0 = np.array( [  8.37,    9.43,   10.74,   11.67,   11.80,   12.48,
                      4.01,    1.08,    3.84,    6.24,    7.54,    8.00 ] )
    a  = np.array( [ -0.0270,  0.0058,  0.1618,  0.0841, -0.0043,  0.2084,
                     0.0970,  0.0712,  0.0393,  0.1158,  0.0567, -0.0540 ] )
    b  = np.array( [ -0.3400, -0.1309,  0.0276, -0.1328, -0.4284, -0.5739,
                     -0.4930, -0.1450, -0.2107, -0.2803, -0.3201, -0.3650 ] )
    c  = np.array( [ -0.0319,  0.0017,  0.0213,  0.0081, -0.0380, -0.0468,
                     -0.0333, -0.0155, -0.0182, -0.0215, -0.0284, -0.0362 ] )
    d  = np.array( [ -0.0056, -0.0021,  0.0076, -0.0003, -0.0071, -0.0023,
                     -0.0026,  0.0014, -0.0053,  0.0015, -0.0032, -0.0112 ] )
    e  = np.array( [ -0.0005, -0.0072, -0.0125, -0.0301, -0.0063, -0.0253,
                     -0.0343, -0.0000, -0.0190, -0.0176, -0.0129, -0.0035 ] )

    x = (90. - lat) * np.cos( np.radians(lon) )
    y = (90. - lat) * np.sin( np.radians(lon) )

    h = ( h0[im] + ( a[im] * x ) + ( b[im] * y ) + ( c[im] * x * y ) +
          ( d[im] * x * x ) + ( e[im] * y * y ) )

#    h = np.where( h < 0., 0., h)
    
    return h
    
def sample_grid(variable='snow_depth', month=None):
    """
    Returns a sample grid for northern hemisphere north of 70 N for a list of
    months.

    variable - snow_depth or swe
    month - list of months
    """

    my_func = {'snow_depth': snow_depth,
               'swe': swe}

    lat, lon = np.linspace(70.,90.,20), np.linspace(0.,359.,360)
    
    if not month:
        month = np.arange(1,13)
    else:
        month = np.array(month)

    x, y = np.meshgrid(lon, lat)

    if month.size == 1:
        da = xr.DataArray(my_func[ftype](x,y,month),
                          coords={'lat': lat, 'lon': lon},
                          dims=['lat', 'lon'])
    else:
        da = xr.DataArray([my_func[ftype](x, y, m) for m in month],
                           coords={'month': month, 'lat': lat, 'lon': lon},
                           dims=['month', 'lat', 'lon'])
    return da

def count_dims(da):
    """
    Wrapper to return number of dims of a DataArray
    """
    return len(da.dims)

def warren_time_series(lat, lon, dates, variable='snow_depth'):
    """
    Generates an xarray DataArray of snow_depth or swe for a grid and
    series of dates.

    Arguments
    ---------
    lat - latitudes 1D or 2D.  If 1D np.meshgrid is used to create 2D grid 
    lon - longitudes 1D or 2D.  If 1D np.meshgrid is used to create 2D grid 
    dates - array of dates - either datetime object or string

    Keywords
    --------
    variable - Variable to generate: snow_depth or SWE.  Default snow_depth

    Returns
    -------
    xarray DataArray object of snow_depth or swe in cm
    """

    my_func = {'snow_depth': snow_depth,
               'swe': swe}

    #if not all([isinstance(d, dt.datetime) for d in dates]):
    #    print ('Expects datetime objects')

    # If lat, lon are vectors, generate 2d grids
    # Need to add code to make sure x and y are DataArrays
    if (count_dims(lat) == 1):
        x, y = np.meshgrid(lon, lat)
    else:
        x, y = lon, lat
        
    if dates.size == 1:
        cube = my_func[variable](x,y,dates.dt.month)
        da = xr.DataArray(cube,
                          coords={'lat': x, 'lon': y},
                          dims=['lat', 'lon'])
    else:
        cube = [my_func[variable](x, y, m) for m in dates.dt.month.values]
        da = xr.concat(cube, dim='time')
        da['time'] = dates

    return da
    
def get_snow_depth(lat, lon, time, no_negative_depths=True):

    cube = [snow_depth(lon, lat, m) for m in time.dt.month.values]
    wsd = xr.concat(cube, dim='time')
    wsd['time'] = time

    if no_negative_depths:
        wsd = wsd.where(wsd > 0., 0.)
        
    return wsd

def plot_snow_depth(da, title='', add_colorbar=True, pngfile=None):
    """
    Plots a snow depth grid

    da - xarray DataArray
    """

    ax = plt.add_axes(projection=ccrs.NorthPolarStereo())
    ax.set_extent([-180.,180.,75.,90.], ccrs.PlateCarree())

    cs = ax.contourf(da.x, da.y, da, levels=np.arange(0,48,2), extend='both')
    cs2 = ax.contour(cs, levels=cs.levels, colors='k')

    ax.clabel(cs2, inline=1, fontsize=10, fmt='%2.0f')
    ax.set_title(title)
    
    if add_colorbar: plt.colorbar(cs)

    if pngfile: plt.savefig(pngfile)

    return ax

