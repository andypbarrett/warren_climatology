#----------------------------------------------------------------------
# Functions to read NSIDC North Polar Stereographic sea ice
# concentration and extent files.
#----------------------------------------------------------------------
import os
import glob
import numpy as np
import datetime as dt

import xarray as xr
from rasterio.warp import transform

from readers.read_grids import read_geotiffs

def get_extent_file_list():
    """Returns list of northern hemisphere extent geotiffs"""
    dirpath = '/disks/sidads_ftp/DATASETS/NOAA/G02135/north/monthly/geotiff'
    return glob.glob(os.path.join(dirpath,'*','N_*_extent_v3.0.tif'))

def date_from_file(filepath):
    return dt.datetime.strptime(filepath.rsplit('/',1)[1].split('_')[1],'%Y%m')

def get_datetime(filelist):
    return [date_from_file(f) for f in filelist]

def get_latlon(da):
    """Calculates lat, lon for grid"""
    ny, nx = len(da['y']), len(da['x'])
    x, y = np.meshgrid(da['x'], da['y'])

    lon, lat = transform(da.crs, {'init': 'EPSG:4326'},
                         x.flatten(), y.flatten())
    lon = np.asarray(lon).reshape((ny,nx))
    lat = np.asarray(lat).reshape((ny,nx))

    da.coords['lon'] = (('y','x'), lon)
    da.coords['lat'] = (('y','x'), lat)

    return

def get_sea_ice_extent(date_from=None, date_to=None,
                       add_land_mask=True, dates=None):
    """
    Wrapper to get sorted DataArray of sea ice extent

    date_from - date to start series YYYY-MM-DD
    date_to   - date to end series   YYYY-MM-DD
    dates     - single date or array of dates [YYYY-MM-DD, YYYY-MM-DD]
    add_land_mask - sets land and coast values to nan
    """

    filelist = get_extent_file_list()
    dates = get_datetime(filelist)
    dates, filelist = map( list, zip(*sorted( list( zip(dates, filelist) ),
                                              key=lambda date: date[0])) )

    #Template to select filelist and dates before reading
    #dates, filelist = map(list, zip( *[(d, f) for d, f in zip(dates, filelist) \
    #                                   if (d >= dt.datetime(1981,1,1)) and \
    #                                   (d <= dt.datetime(1981,12,31))] ) )
    
    da = read_geotiffs(filelist, concat_dim='time')
    da['time'] = dates

    get_latlon(da)

    if add_land_mask:
        da = da.where(da < 253)

    # make time selection
    if date_from and (not date_to): da = da.sel(time=slice(date_from,None))
    if (not date_from) and date_to: da = da.sel(time=slice(None,date_to))
    if date_from and date_to: da = da.sel(time=slice(date_from,date_to))
    
    return da

def get_psn_coords(coords='both', resolution='25'):
    """
    Gets North Polar Stereo latitude and longitude grids
    """
    dirpath = '/disks/sidads_ftp/pub/DATASETS/seaice/polar-stereo/tools/'
    latpath = os.path.join(dirpath, 'psn{:2s}lats_v3.dat'.format(resolution))
    lonpath = os.path.join(dirpath, 'psn{:2s}lons_v3.dat'.format(resolution))
    if (coords == 'lats') or (coords == 'both'):
        lats = xr.DataArray(np.fromfile(latpath, 'int32').reshape(448,304)/100000.,
                            dims=['x','y'])
    if (coords == 'lons') or (coords == 'both'):
        lons = xr.DataArray(np.fromfile(lonpath, 'int32').reshape(448,304)/100000.,
                            dims=['x','y'])
    if (coords == 'lats'):
        return lats
    elif (coords == 'lons'):
        return lons
    elif (coords == 'both'):
        return (lons, lats)

    
def get_psn_area(resolution='25'):
    """
    Gets North Polar Stereo cell areas and puts them into DataArray

    resolution - 25, 12, 06
    """
    dirpath = '/disks/sidads_ftp/pub/DATASETS/seaice/polar-stereo/tools/'
    filepath = os.path.join(dirpath, 'psn{:2s}area_v3.dat'.format(resolution))
    data = xr.DataArray(np.fromfile(filepath, 'int32').reshape(448,304)/1000.,
                        dims=['x','y'])

    return data
    
