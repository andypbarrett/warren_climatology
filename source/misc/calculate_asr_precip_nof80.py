import numpy as np
import xarray as xr
import matplotlib.pyplot as plt
import pandas as pd
import calendar
import os
import cartopy.crs as ccrs
import datetime as dt

def days_in_month(time):
    """
    Returns the number of days in each month for a numpy Datetime64 object.  The days in month
    are returned as an xarray DataArray with the original time as coords.

    The Datetime64 object is converted to a pandas datetime index to get month and year.
    """

    import xarray as xr
    import pandas as pd
    import calendar

    time_index = pd.DatetimeIndex( ds['time'].values )

    return xr.DataArray([calendar.monthrange(y, m)[1] for y, m in zip(time_index.year, time_index.month)],
                        coords=[ds['time']])

# Get the data
diri = '/disks/arctic5_raid/abarrett/ASR'
fili = 'asr30km.fct.2D.*.month.nc'

def read_netcdfs(files, dim):

    from glob import glob
    import xarray as xr

    # glob expands paths with * to a list of files, like the unix shell
    paths = sorted(glob(files))
    datasets = [xr.open_dataset(p) for p in paths]


    time = pd.date_range('2000-01-01','2012-12-31',freq='M')

    combined = xr.concat(datasets, pd.Index(time, name='time'))
    return combined

ds = read_netcdfs(os.path.join(diri,fili), dim='time')

# Calculate annual total
annualTotal = ds['RAINNC'].groupby('time.year').sum(dim='time')

# Extract mean for north of 80 N
annualMean = annualTotal.mean(dim='year')

tmp = np.cos(ds['XLAT']*np.pi/180.)
weight = tmp.where(ds['XLAT'] > 80.) / tmp.where(ds['XLAT'] > 80.).sum()

arctic_annTotal = annualTotal.where(ds['XLAT'] >= 80.).mean(dim=['south_north','west_east'])
arctic_annTotal.name = 'precAnn'

# Change year coordinate to datetime
new_time = [dt.datetime(y, 2, 1) for y in arctic_annTotal['year']]
new_da = arctic_annTotal.rename({'year': 'time'})
new_da['time'] = new_time

new_da.to_netcdf('/home/apbarret/data/SnowOnSeaIce/ASR.PRECTOT.season.2000to2012.Nof80.nc')

annualTotal.to_netcdf('/home/apbarret/data/SnowOnSeaIce/ASR.PRECTOT.season.2000to2012.nc')
