#----------------------------------------------------------------------
# Plots climatologies of precip stats
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
        'MERRA2': '/disks/arctic5_raid/abarrett/MERRA2/daily/PRECTOT/MERRA2.tavg1_2d_flx_Nx.PRECIP_STATS.accumulation.annual.Nh50km.nc4',}

maskFile = '/home/apbarret/src/utilities/data/arctic_mask.ocean.Nh50km.nc'

def get_data(reanalysis, field):
    """
    Get specified PRECIP_STAT field for a given reanalysis
    """
    ds = xr.open_dataset(fili[reanalysis])
    da = ds[field]
    if reanalysis == 'JRA55': da = da*0.1
    year = ds['time'].dt.year
    return da.isel( time=( (year >= 1981) & (year <= 2015) ) ).mean(dim='time')
    
def plot_precip_stats():

    from plotutils import EASE_North

    field = 'precTot'
    
    map_proj = EASE_North()
    extent = [-9036842.762500, 9036842.762500, -9036842.762500, 9036842.762500]
    lim = 3000000
    
    bounds = np.arange(50,1000.,50)
    norm = mcolors.BoundaryNorm(boundaries=bounds, ncolors=256)

    fig = plt.figure(figsize=(15,7))
    
    # Plot field
    ax = []
    for ip, renm in enumerate(list(fili.keys())):

        print ('Plotting {:s}'.format(renm))

        var = get_data(renm, field)
        print (var.min(), var.max())
        
        ax.append( plt.subplot(2, 3, ip+1, projection=map_proj, xlim=lim, ylim=lim) )
        ax[ip].set_extent([-180.,180.,65.,90.], ccrs.PlateCarree())
        img = ax[ip].imshow(var, norm=norm, cmap='YlGnBu', 
                            interpolation='none', origin='upper',
                            extent=extent, transform=map_proj)
        ax[ip].coastlines()
        ax[ip].gridlines()
        ax[ip].set_title(renm)

    fig.colorbar(img, ax=ax[-1], extend='both', orientation='vertical')
    
    fig.savefig('arctic_precipitation.accumulation_period.climatology.{:s}.png'.format(field))

    return

if __name__ == "__main__":

    import argparse

    #parser = argparse.ArgumentParser(description="Calculates time series of AO average precip stats")
    #parser.add_argument('reanalysis', type=str, help='Reanalysis to process')
    #args = parser.parse_args()

    plot_precip_stats() #(args.reanalysis)
    
