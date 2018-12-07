#----------------------------------------------------------------------
# Utility functions to download and process MERRA2 data using PYDAP
#
#----------------------------------------------------------------------

import datetime as dt
import numpy as np

def get_dataset(url):

    from pydap.client import open_url                                  
    from pydap.cas.urs import setup_session                            
    
    user = 'apbarret'
    pswd = 'T0talBollocks'
    
    session = setup_session(user, pswd, check_url=url)
    dataset = open_url(url, session=session)
    
    return dataset

def pydap2xarray(dataset, varname, url=None,
                 level=[1000., 925., 850., 700., 500., 300.]):
    
    import xarray as xr
    import datetime as dt
    
    from collections import OrderedDict
    
    var = dataset[varname]
    time = dataset['time']
    lat  = dataset['lat']
    lon  = dataset['lon']

    if var.ndim > 3:
        print ('HERE')
        lev = dataset['lev']
        da = xr.DataArray(var[:], coords=[time[:],lev[:],lat[:],lon[:]],
                          dims=['time','lev','lat','lon'],
                          attrs=var.attributes, name=varname)
        da['lev'].attrs = OrderedDict([('long_name', lev.attributes['long_name']),
                                       ('units', lev.attributes['units'])])
        if level: da = da.sel(lev=level)
    else:
        da = xr.DataArray(var[:], coords=[time[:],lat[:],lon[:]],
                          dims=['time','lat','lon'],
                          attrs=var.attributes, name=varname)
    da['lat'].attrs = OrderedDict([('long_name', 'latitude'), ('units', 'degrees_north')])
    da['lon'].attrs = OrderedDict([('long_name', 'longitude'), ('units', 'degrees_east')])
    

    # To avoid conflicts between _FillValue and missing_value attributes when file is read
    da.attrs.pop('fmissing_value')
    da.attrs.pop('missing_value')

    if (np.array(da.shape) == 1).any(): da = da.squeeze(drop=True)

#    ds = da.to_dataset()
#    ds.attrs['created_by'] = 'Andrew P. Barrett <apbarret@nsidc.org'
#    ds.attrs['created'] = dt.datetime.now().strftime('%Y%m%d')
#    if url: ds.attrs['source'] = url
    
    return da

def get_urlList(list_file):
    '''
    Gets a list of url for the MERRA2 OpenDAP server

    This is a quick and dirty fix to the problem of querying the server for a list of 
    files for a given dataset.  For now, I generate the list using the Subsetter and
    extract file names from that list.
    '''

    with open(list_file) as f:
        lines = f.readlines()

    filenames = [l.strip() for l in lines]

    return filenames

def parse_date(datestr):
    if len(datestr) == 6:
        date = dt.datetime.strptime(datestr, '%Y%m')
    else:
        date = dt.datetime.strptime(datestr, '%Y%m%d')
    return date

def subset_urlList(urlList, begin, end):
    import datetime as dt
    import re
    import numpy as np

    if begin:
        dbeg = dt.datetime.strptime(begin, '%Y%m%d')
    else:
        dbeg = dt.datetime(1978,12,31)
    if end:
        dend = dt.datetime.strptime(end, '%Y%m%d')
    else:
        dend = dt.datetime.now()
    
    m = re.compile('\.(\d{6,8})\.')
    date = np.array([parse_date(m.search(f).groups()[0]) for f in urlList])

    dummy = np.array(urlList)

    return dummy[(date >= dbeg) & (date <= dend)]
    
def hour2day(daHr):
    '''
    Calculates total precipitation and carries attributes
    
    daHr - DataArray containing hourly data
    
    Returns: DataArray with daily total
    '''
    
    # Check if hourly values are rate or a total
    if daHr.attrs['units'] == 'kg m-2 s-1':
        daDay = daHr.sum(dim='time')*3600.
    else:
        daDay = daHr.sum(dim='time')
        
    daDay.attrs = daHr.attrs
    if daHr.attrs['units'] == 'kg m-2 s-1':
        daDay.attrs['units'] = 'mm'

    if 'begin_date' in daHr.time.attrs:
        daDay.attrs['time'] = str(daHr.time.attrs['begin_date'])
    
    return daDay
