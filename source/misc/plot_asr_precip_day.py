import numpy as np
import xarray as xr
import pandas as pd
import matplotlib.pyplot as plt
import os

def days_in_month(time):
    """
    Returns the number of days in each month for a numpy Datetime64 object.  The days in month
    are returned as an xarray DataArray with the original time as coords.

    The Datetime64 object is converted to a pandas datetime index to get month and year.
    """
    import xarray as xr
    import pandas as pd
    import calendar

    time_index = pd.DatetimeIndex( time.values )

    return xr.DataArray([calendar.monthrange(y, m)[1] for y, m in zip(time_index.year, time_index.month)],
                        coords=[time['time']])

diri = '/disks/arctic5_raid/abarrett/ASR'
fili = 'asr30km.fct.2D.200001to201212.mon.nc'
ds_mon = xr.open_dataset(os.path.join(diri,fili))

# Convert from mean of daily totals to monthly total
days_in_mon = days_in_month(ds_mon['time'])
monthTotal = ds_mon['RAINNC']*days_in_mon*8.

ds = xr.open_dataset('/disks/arctic5_raid/abarrett/ASR/asr30km.fct.2D.200001.day.nc')

total_prcp = ds['RAINNC'].sum(dim=['Time'])

print total_prcp.where(ds['XLAT'] > 80.).max()
print monthTotal.where(ds_mon['XLAT'] > 80.).max()

fig, ax = plt.subplots(1, 2, figsize=(25,10))

levels = np.linspace(0,550.,12.)
total_prcp.plot(ax=ax[0], levels=levels)
monthTotal[0,:,:].plot(ax=ax[1], levels=levels)

#ds['RAINNC'].where(ds['XLAT'] > 80.).mean(dim=['south_north', 'west_east']).plot(ax=ax)

plt.show()


