import matplotlib
matplotlib.use('agg')

from utilities.seaice import get_sea_ice_extent
from warren_climatology.warren_climatology import get_snow_depth, plot_snow_depth

import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cfeature
import numpy as np

import calendar

print ('Getting SIE')
sie = get_sea_ice_extent(date_from='1981-01-01', date_to='1981-12-31')

print ('Estimating snow depth')
wsd = get_snow_depth(sie.lat, sie.lon, sie.time)
#wsd = wsd.where(wsd > 0., 0.) # Set -ve snow depth to 0.
wsd = wsd.where(sie == 1) # Set cells wehere no sea ice to NaN


month_names = calendar.month_name

fig = plt.figure(figsize=(8,11))

for i, mon in enumerate( range(1,13) ): 
    ax = fig.add_subplot(4,3,mon, projection=ccrs.NorthPolarStereo())
#    ax = fig.add_subplot(4,3,mon, projection=ccrs.NorthPolarStereo(central_longitude=-45.)) # Doesn't work

    ax.set_extent([-180.,180.,65.,90.], ccrs.PlateCarree())

    cs = ax.contourf(wsd.x, wsd.y, wsd[i,:,:], levels=np.arange(0,48,2), extend='both')
    cs2 = ax.contour(cs, levels=cs.levels, colors='k')

    #ax.add_feature(cfeature.LAND, facecolor='0.3')
    
    ax.clabel(cs2, inline=1, fontsize=10, fmt='%2.0f')
    ax.set_title(month_names[mon])

#fig.colorbar(cs)

plt.savefig('test.png')

