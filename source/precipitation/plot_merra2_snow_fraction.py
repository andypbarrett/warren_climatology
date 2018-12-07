import os, glob
import re
import calendar

import numpy as np
import xarray as xr
import datetime as dt

import matplotlib.pyplot as plt
import matplotlib.colors as mcolors

import cartopy.crs as ccrs
import cartopy.feature as cfeature

from plotutils import EASE_North

def get_month_snowfall():
    """Calculates monthly mean snowfall and snowdays"""

    dirpath = '/disks/arctic5_raid/abarrett/MERRA2/daily/PRECSNO'
    fileGlob = glob.glob( os.path.join(dirpath,
                                       '????',
                                       '??',
                                       'MERRA2_100.tavg1_2d_flx_Nx.PRECSNO_STATS.??????.month.Nh50km.nc4') )

    p = re.compile('\.(\d{6})\.month')
    
    ds = xr.open_mfdataset(sorted(fileGlob), concat_dim='time', data_vars='different')
    time = [dt.datetime.strptime(p.search(f).groups(1)[0],'%Y%m') for f in sorted(fileGlob)]
    ds.coords['time'] = time

    return ds

def get_month_prectot():
    """Calculates monthly mean snowfall and snowdays"""

    dirpath = '/disks/arctic5_raid/abarrett/MERRA2/daily/PRECTOT'
    fileGlob = glob.glob( os.path.join(dirpath,
                                       '????',
                                       '??',
                                       'MERRA2.tavg1_2d_flx_Nx.PRECIP_STATS.??????.month.Nh50km.nc4') )

    p = re.compile('\.(\d{6})\.month')
    
    ds = xr.open_mfdataset(sorted(fileGlob), concat_dim='time', data_vars='different')
    time = [dt.datetime.strptime(p.search(f).groups(1)[0],'%Y%m') for f in sorted(fileGlob)]
    ds.coords['time'] = time

    return ds

def plot_snowday(da, nrow, ncol, ipos, title=''):

    map_proj = EASE_North()
    extent = [-9036842.762500, 9036842.762500, -9036842.762500, 9036842.762500]
    lim = 3000000

    bounds = np.linspace(0.,1.,11)
    norm = mcolors.BoundaryNorm(boundaries=bounds, ncolors=256)
    cmap = 'YlGnBu'
    
    ax = plt.subplot(nrow, ncol, ipos, projection=map_proj, xlim=lim, ylim=lim)
    ax.set_extent([-180.,180.,70.,90.], ccrs.PlateCarree())

    img = ax.imshow(da, norm=norm, cmap=cmap, interpolation='none',
                    origin='upper', extent=extent, transform=map_proj)
    ax.coastlines()
    ax.set_title(title)

    return ax, img

def main():

    print ('Getting snowfall...')
    snowfall = get_month_snowfall()
    snow = snowfall['snow'].where(snowfall['snow'] > 0.)
    
    print ('Getting prectot...')
    prectot = get_month_prectot()
    precip = prectot['prectot'].where(prectot['prectot'] > 0.)
    
    snow_fraction = snow/precip
    snow_fraction_month = snow_fraction.groupby('time.month').mean(dim='time')

    snow_fraction_month.load()
    
    fig = plt.figure(figsize=(8,11))

    ax = []
    for month in snow_fraction_month.month.values:
        axis, img = plot_snowday(snow_fraction_month.sel(month=month), 4, 3, month,
                                 title=calendar.month_abbr[month])
        ax.append(axis)
        
    fig.subplots_adjust(bottom=0.1)
    cbar_ax = fig.add_axes([0.15, 0.05, 0.7, 0.03])
    fig.colorbar(img, cax=cbar_ax, extend='neither', orientation='horizontal')

    #plt.show()
    fig.savefig('merra2_monthly_mean_snow_fraction.png')
    

    print (snow_fraction)

if __name__ == "__main__":
    main()
    

