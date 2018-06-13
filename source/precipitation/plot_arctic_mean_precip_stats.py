import matplotlib
matplotlib.use('Agg')

import xarray as xr
import matplotlib.pyplot as plt
import datetime as dt
import pandas as pd

import os

def get_data(fili,varName):
    ds = xr.open_dataset(fili)
    da = ds[varName]
    da = da.rename({'ncl0': 'time'})
    if varName == 'cfsr2':
        da['time'] = pd.date_range('2012-01-01', periods=da.shape[0], freq='AS')
    elif (varName == 'merra') | (varName == 'jra55'):
        da['time'] = pd.date_range('1980-01-01', periods=da.shape[0], freq='AS')
    else:
        da['time'] = pd.date_range('1981-01-01', periods=da.shape[0], freq='AS')
    return da

diri = '/home/apbarret/src/SnowOnSeaIce/data'
cfsr_fili = 'cfsr_arctic_mean_prectot_arctic_ocean.nc'
erai_fili = 'era_interim_arctic_mean_prectot_arctic_ocean.nc'
mer2_fili = 'merra2_arctic_mean_prectot_arctic_ocean.nc'
cfs2_fili = 'cfsr2_arctic_mean_prectot_arctic_ocean.nc'
merr_fili = 'merra_arctic_mean_prectot_arctic_ocean.nc'
ja55_fili = 'jra55_arctic_mean_prectot_arctic_ocean.nc'

cfsr_prectot = get_data(os.path.join(diri, cfsr_fili), 'cfsr')
erai_prectot = get_data(os.path.join(diri, erai_fili), 'erai')
mer2_prectot = get_data(os.path.join(diri, mer2_fili), 'merra2')
cfs2_prectot = get_data(os.path.join(diri, cfs2_fili), 'cfsr2')
merr_prectot = get_data(os.path.join(diri, merr_fili), 'merra')
ja55_prectot = get_data(os.path.join(diri, ja55_fili), 'jra55')

print (merr_prectot)
print (ja55_prectot)

fig, ax = plt.subplots(figsize=(15,8))

cfsr_prectot.plot(ax=ax, label='CFSR', color='green', linewidth=3)
erai_prectot.plot(ax=ax, label='ERA-Interim', color='red', linewidth=3)
mer2_prectot.plot(ax=ax, label='MERRA2', color='blue', linewidth=3)
cfs2_prectot.plot(ax=ax, label='CFSR2', color='lightgreen', linewidth=3)
merr_prectot.plot(ax=ax, label='MERRA', color='pink', linewidth=3)
ja55_prectot.plot(ax=ax, label='JRA55', color='purple', linewidth=3)

ax.set_ylim(0.,400.)
ax.set_xlim(dt.datetime(1979,1,1), dt.datetime(2017,12,31))

ax.set_title('August to April Total Precipitation', fontsize=20)
ax.set_ylabel('mm', fontsize=20)
ax.set_xlabel('')
ax.tick_params(labelsize=20)

ax.legend(fontsize=18, bbox_to_anchor=(0.6,0.01), loc=3, borderaxespad=0, ncol=2)

fig.savefig('reanalysis_arctic_mean_precip_stats.png')



