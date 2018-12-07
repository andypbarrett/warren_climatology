# Utility routines for processing reanalysis precipitation data for
# the Snow on Sea Ice project

import numpy as np
import xarray as xr
import glob
import os

from constants import filepath, vnamedict

def _glob_precip_stats_dirpath(reanalysis):
    """
    Generates glob dir path
    """
    fmt = os.path.join( os.path.split( os.path.split( filepath[reanalysis]['path'] )[0] )[0], '????', '??')
    return fmt.format('PRECTOT')

def _glob_precip_stats_fname(reanalysis):
    """
    Generates glob filename
    """
    fname = filepath[reanalysis]['ffmt'].format('PRECIP_STATS','????')
    fname = fname.replace('.nc','.month.Nh50km.nc')
    return fname

def glob_precip_stats(reanalysis):
    """
    Returns a list of files for a given reanalysis and variable using glob
    
    NB: I think I might have to hardcode the file formats

    reanalysis - ERAI, CFSR, MERRA, MERRA2
    variable - name of variable
    
    grid - e.g. Nh50km
    """

    globpath = _glob_precip_stats_dirpath(reanalysis)
    globfile = _glob_precip_stats_fname(reanalysis)
    #fileList = glob.glob( os.path.join( globpath, globfile) )
    return os.path.join( globpath, globfile)

def make_filepath(reanalysis, variable, date, grid=None):
    '''
    Generates a filepath for a given reanalysis variable for a given date
    
    reanalysis - name of reanalysis
    variable - my standard variable name
    date - date string - can have wildcards
    
    returns - filepath string
    '''

    from constants import filepath, vnamedict

    fp = os.path.join(filepath[reanalysis]['path'].format(vnamedict[reanalysis][variable]['name'], date.year, date.month),
                       filepath[reanalysis]['ffmt'].format(vnamedict[reanalysis][variable]['name'], date.strftime('%Y%m')))

    if grid:
        #if (reanalysis == 'CFSR') | (reanalysis == 'CFSR2'):
        #    fp = fp.replace('.nc','.{:s}.nc'.format('EASE_NH50km'))
        #else:
        #    fp = fp.replace('.nc', '.{:s}.nc'.format(grid))
        fp = fp.replace('.nc', '.{:s}.nc'.format(grid))
        
    return fp

def make_outfile(fili, reanalysis, variable, version=None):
    from constants import vnamedict
    import re

    new_varname = {'PRECIP': '.PRECIP_STATS',
                   'SNOW': '.PRECSNO_STATS',}
    filo = fili
    filo = re.sub('(?<=MERRA)[_]*\?0+','',filo)
    filo = re.sub('(?<=MERRA2)[_]*\?0+','',filo)

    filo = filo.replace('.'+vnamedict[reanalysis][variable]['name'],new_varname[variable]).replace('??.','.month.').replace('.day.','.month.')
    if version: filo = filo.replace('.nc','.v{:s}.nc'.format(version))
    
    return filo

def make_fileList(reanalysis, variable, date_range, grid=None):
    '''
    Generates a list of filepaths for a given reanalysis and variable for a date range.
    The code deals with CFSR* spanning two products.

    reanalysis - name of reanalysis
    variable   - my standard variable name
    date_range - tuple of dates in format (yyyymmdd, yyyymmdd)
    
    returns - filepath string
    '''

    from pandas import date_range as pd_date_range
    import datetime as dt
    
    filelist = []
    for date in pd_date_range(date_range[0], date_range[1], freq='M'):
        if (reanalysis == 'CFSR') & (date >= dt.datetime(2011,1,1)):
            filelist.append(make_filepath('CFSR2', variable, date, grid=grid))
        else:
            filelist.append(make_filepath(reanalysis, variable, date, grid=grid))

    return filelist

def date_from_filename(fname):
    '''Extracts the YYYYMM from a filename and returns a datetime object'''
    import re
    import datetime as dt

    m = re.search('\.(\d{6})[\?\.]', fname).groups()[0]
    return dt.datetime.strptime(m, '%Y%m')

def make_time_coordinate(fileGlob):
    '''
    Generates a time coordinate using file times stamps
    '''
    import calendar
    import pandas as pd
    
    date = date_from_filename(fileGlob)
    last_day = calendar.monthrange(date.year, date.month)[1]
    
    start_date = '{:4d}{:02d}{:02d}'.format(date.year, date.month, 1)
    end_date = '{:4d}{:02d}{:02d}'.format(date.year, date.month, last_day)

    return xr.IndexVariable('time',pd.date_range(start_date, end_date, freq='D'))

                            
def read_month(fileGlob, reanalysis, variable):
    '''
    Gets a xarray DataArray of days in month for a given variable

    Need to add time dimension if I want to do something fancy
    '''

    from constants import vnamedict

    vname = vnamedict[reanalysis][variable]

    fileList = glob.glob(fileGlob)
    with xr.open_mfdataset(fileList, concat_dim='time', data_vars='different') as ds:

        # To deal with 2016 ERA-Interim data
        if (reanalysis == 'ERA-Interim') & (date_from_filename(fileGlob).year > 2015):
            ds.rename({'tp': 'PRECTOT', 'latitude': 'lat', 'longitude': 'lon'}, inplace=True)
        ds[vname['name']] = ds[vname['name']] * vname['scale'] # Scale to mm and change units

        ds.set_coords(['latitude','longitude'], inplace=True)
        
        #if 'latitude' in ds: ds['latitude'] = ds['latitude'][0,:,:]
        #if 'longitude' in ds: ds['longitude'] = ds['longitude'][0,:,:]
        
        if 'time' not in ds.coords.keys(): ds.coords['time'] = make_time_coordinate(fileGlob)
        
        #ds.load()
        
    return ds

def apply_threshold(da, threshold=1.):
    return xr.DataArray(np.where(da.values > 1., da.values, 0.),
                        coords=da.coords,
                        dims=da.dims,
                        name=da.name,
                        attrs=da.attrs)
    
def wetday_mean(da, threshold=1.):
    '''
    Returns mean precipitation rate for wet days

    wetdays are defined as days with rain rate greater than a threshold (default = 1. mm/day)

    da - data array containing precipitation
    threshold - threshold to distinguish wet days (default 1 mm/day)
    
    Returns 2D data array with lat and lon dimensions
    '''
    return apply_threshold(da, threshold=threshold).mean(dim='time')

def wetdays(da, threshold=1.):
    '''
    Returns frequency of wet days

    wetdays are defined as days with rain rate greater than a threshold (default = 1. mm/day)

    da - data array containing precipitation
    threshold - threshold to distinguish wet days (default 1 mm/day)
    
    Returns 2D data array with lat and lon dimensions
    '''
    ntot = da.shape[0]
    nwet = da.where(da > threshold).count(dim='time')
    return nwet.astype(float)/float(ntot)

def wetday_max(da, threshold=1.):
    '''
    Returns maximum precipitation rate for wet days (same as max of dataarray)

    wetdays are defined as days with rain rate greater than a threshold (default = 1. mm/day)

    da - data array containing precipitation
    threshold - threshold to distinguish wet days (default 1 mm/day)
    
    Returns 2D data array with lat and lon dimensions
    '''
    return da.max(dim='time')

def wetday_total(da, threshold=1.):
    '''
    Returns total precipitation rate for wet days.  This is not the same as the sum all precipitation.

    wetdays are defined as days with rain rate greater than a threshold (default = 1. mm/day)

    da - data array containing precipitation
    threshold - threshold to distinguish wet days (default 1 mm/day)
    
    Returns 2D data array with lat and lon dimensions
    '''
    return apply_threshold(da, threshold=threshold).sum(dim='time')

def all_total(da):
    return da.sum(dim='time')


def arbitSum(ds, dateStart, dateEnd):
    sub = ds.sel(time=slice(dateStart,dateEnd))
    nt = sub.time.size
    it = np.floor(nt/2.).astype(int)
    result = sub.sum(dim='time')
    result = result.expand_dims('time', axis=0)
    result.coords['time'] = sub['time'][it]
    return result
    




    

