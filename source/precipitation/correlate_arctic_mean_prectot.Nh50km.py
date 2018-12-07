import xarray as xr
import matplotlib.pyplot as plt
import datetime as dt
import pandas as pd

import os

fili = {'CFSR': '/disks/arctic5_raid/abarrett/CFSR/PRATE/CFSR.flxf06.gdas.PRECIP_STATS.accumulation.annual.Nh50km.AOSeries.nc',
        'ERAI': '/disks/arctic5_raid/abarrett/ERA_Interim/daily/PRECTOT/era_interim.PRECIP_STATS.accumulation.annual.Nh50km.AOSeries.nc',
        'JRA55': '/projects/arctic_scientist_data/Reanalysis/JRA55/daily/TOTPREC/JRA55.fcst_phy2m.PRECIP_STATS.accumulation.annual.Nh50km.AOSeries.nc',
        'MERRA': '/disks/arctic5_raid/abarrett/MERRA/daily/PRECTOT/MERRA.prod.PRECIP_STATS.assim.tavg1_2d_flx_Nx.accumulation.annual.Nh50km.AOSeries.nc4',
        'MERRA2': '/disks/arctic5_raid/abarrett/MERRA2/daily/PRECTOT/MERRA2.tavg1_2d_flx_Nx.PRECIP_STATS.accumulation.annual.Nh50km.AOSeries.nc4',}

def get_data(fili,varName):
    ds = xr.open_dataset(fili)
    da = ds[varName]
    return da

df = pd.concat([get_data(fili['CFSR'], 'precTot').to_dataframe('CFSR'),
                get_data(fili['ERAI'], 'precTot').to_dataframe('ERAI'),
                get_data(fili['MERRA2'], 'precTot').to_dataframe('MERRA2'),
                get_data(fili['MERRA'], 'precTot').to_dataframe('MERRA'),
                get_data(fili['JRA55'], 'precTot').to_dataframe('JRA55')], axis=1)

print (df)

df_corr = df.corr()
print (df_corr.where(df_corr < 1.).mean())

print (df['1981':'2015'].mean(axis=0))
print (df['1981':'1991'].mean(axis=0))

#df.plot()
#plt.show()

df.to_csv('arctic_ocean_reanalysis_prectot_nh50km.csv')




