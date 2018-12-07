#----------------------------------------------------------------------
# Calculates long-term probability grid cells are ice covered (> 15%)
# in each month.
#----------------------------------------------------------------------

#import matplotlib
#matplotlib.use('agg')

import numpy as np
import datetime as dt
import os, glob

from warren_climatology.warren_climatology import snow_depth
    
def main():

    # Get sea ice extent grids
    da = get_sie()
    da = da.sel(time=slice('1981-01-01','2010-12-31'))
    da = da.where(da < 253)
    
    print (da.min(), da.max())

    print (da.lat.dims.shape)
    
    """
    numcells = da.where(da['lat'] > 80.).sum(dim=['x','y'])
    numcells.groupby('time.month').mean(dim='time').plot()
    plt.title('# Ice covered grid cells north of 80 N') 
    plt.show()
    plt.savefig('sic_north_of_80.png')
    """
    
    return

if __name__ == "__main__":
    main()
    

