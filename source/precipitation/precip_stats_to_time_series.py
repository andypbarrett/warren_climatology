#----------------------------------------------------------------------
# Generates time series of accumulation season period averaged over
# Arctic Ocean domain.
#
#----------------------------------------------------------------------

import matplotlib

matplotlib.use('Agg')

import xarray as xr
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import cartopy.crs as ccrs
import cartopy.feature as cfeature
import numpy as np

fili = {'CFSR': '/disks/arctic5_raid/abarrett/CFSR/PRATE/CFSR.flxf06.gdas.PRECIP_STATS.accumulation.annual.Nh50km.nc',
        'ERAI': '/disks/arctic5_raid/abarrett/ERA_Interim/daily/PRECTOT/era_interim.PRECIP_STATS.accumulation.annual.Nh50km.nc',
        'JRA55': '/projects/arctic_scientist_data/Reanalysis/JRA55/daily/TOTPREC/JRA55.fcst_phy2m.PRECIP_STATS.accumulation.annual.Nh50km.nc',
        'MERRA': '/disks/arctic5_raid/abarrett/MERRA/daily/PRECTOT/MERRA.prod.PRECIP_STATS.assim.tavg1_2d_flx_Nx.accumulation.annual.Nh50km.nc4',
        'MERRA2': '/disks/arctic5_raid/abarrett/MERRA2/daily/PRECTOT/MERRA2.tavg1_2d_flx_Nx.PRECIP_STATS.accumulation.annual.Nh50km.nc4',
        'ERA5': '/projects/arctic_scientist_data/Reanalysis/ERA5/daily/TOTPREC/era5.single_level.PRECIP_STATS.accumulation.annual.nc4'}

maskFile = '/home/apbarret/src/utilities/data/arctic_mask.ocean.Nh50km.nc'

def precip_stats_to_climatology(reanalysis):

    ds = xr.open_dataset(fili[reanalysis])
    mask = xr.open_dataset(maskFile)

    print (ds)

    if reanalysis == 'CFSR': ds.rename({'row': 'x', 'col': 'y'}, inplace=True)
    
    if reanalysis == 'JRA55':
        ds['precTot'] = ds['precTot']*0.1
        ds['wetdayTot'] = ds['wetdayTot']*0.1
        ds['wetdayAve'] = ds['wetdayAve']*0.1
        
    dsMsk = ds * mask['ocean']
    dsSeries = dsMsk.mean(dim=['x','y'])
    
    filo = fili[reanalysis].replace('.nc','.AOSeries.nc')
    print ('Writing time series to {:s}'.format(filo))
    dsSeries.to_netcdf(filo)
    
    return

if __name__ == "__main__":

    import argparse

    parser = argparse.ArgumentParser(description="Calculates time series of AO average precip stats")
    parser.add_argument('reanalysis', type=str, help='Reanalysis to process')
    args = parser.parse_args()

    precip_stats_to_climatology(args.reanalysis)
    
