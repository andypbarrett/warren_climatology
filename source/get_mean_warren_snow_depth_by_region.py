import matplotlib
matplotlib.use('agg')
               
import matplotlib.pyplot as plt
import pandas as pd
import xarray as xr
import numpy as np
import os

from affine import Affine

from utilities.seaice import get_sea_ice_extent
from warren_climatology.warren_climatology import get_snow_depth, plot_snow_depth

code = {
        'Bering': 3,
        'Beaufort': 13,
        'Chukchi': 12,
        'East_Siberian': 11,
        'Laptev': 10,
        'Kara': 9,
        'Barents': 8, 
        'Central_Arctic': 15,
        'Greenland': 7,
        'CAA': 14,
        'Labrador': 6,
        'Hudson Bay': 4,
        'Okhutsk': 2,
        }

def get_mask():
    """
    Gets PSN Arctic region mask
    """
    src_dir = '/disks/sidads_ftp/DATASETS/NOAA/G02135/seaice_analysis'
    src_file = 'Arctic_region_mask_Meier_AnnGlaciol2007.msk'
    nrow, ncol = (448, 304) 

    mask = np.fromfile( os.path.join(src_dir, src_file), dtype='byte').reshape(nrow,ncol)
#    msk = np.rot90(msk,2)
#   msk = np.flipud(msk)
    geo_transform = [-3850000.000, 25000., 0., 5850000.000, 0., -25000.] # GDAL style geotransform
    transform = Affine.from_gdal(*geo_transform)

    x, _ = (np.arange(ncol) + 0.5, np.zeros(ncol) + 0.5) * transform
    _, y = (np.zeros(nrow) + 0.5, np.arange(nrow) + 0.5) * transform
#    x = [(a * (ic, 0))[0] for ic in np.arange(ncol)]
#    y = [(a * (0, ir))[1] for ir in np.arange(nrow)]

    da = xr.DataArray(mask, coords={'x': x, 'y': y}, dims=['y', 'x'])

    #da = xr.DataArray(msk, dims=['y','x'])
    
    return da


def main(verbose=False):

    # Get sea ice cube
    if verbose: print ('Getting sea ice cube')
    sie = get_sea_ice_extent()

    # Estimate snow depth
    if verbose: print ('Estimating snow depth for cube')
    wsd = get_snow_depth(sie.lat, sie.lon, sie.time)

    # Mask out snow where sea ice extent < 15%
    wsd = wsd.where(sie == 1) # == 0 set to NaN

    # Get region masks
    mask = get_mask()
#    mask['x'] = wsd['x'] # this is a fix to make grids match.  Not sure if issue is
#    mask['y'] = wsd['y'] # with how xray deals with rasterio affine of NSIDC definition
    
    # Get region means for Beaufort, Chukchi, East Siberian, Laptev, Kara, Barent and
    # Central Arctic
    if verbose: print ('Getting regional mean snow depths')
    regions_list = ['Beaufort', 'Chukchi', 'East_Siberian', 'Laptev',
                    'Kara', 'Barents', 'Central_Arctic']
    region_dict = {region: wsd.where(mask == code[region]).mean(dim=['x','y']).to_series()
                   for region in regions_list}
    
    # Calculate snow depth > 80 N
    if verbose: print ('Getting mean snow depth north of 80 N')
    region_dict['North_of_80'] = wsd.where(wsd.lat >= 80.).mean(dim=['x','y']).to_series()

    df = pd.DataFrame(region_dict)

#    print (df)
    df.to_csv('mean_warren_snow_depth_by_region.csv')

if __name__ == "__main__":
    main(verbose=True)
    

