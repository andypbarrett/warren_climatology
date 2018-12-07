import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cfeature

import xarray as xr
import numpy as np
import os

from pinpoint.coord_converter import column_row_from_lat_long
from readers.npsnow import read_yang_updated

def makeGrid():
    """
    Generates a xarray grid for testing
    """
    nx = 360
    ny = 360
    return xr.DataArray(np.zeros([nx,ny]),
                        coords={'row': np.arange(0,nx),
                                'col': np.arange(0,ny)},
                        dims=['row','col'])
    
def latlon2colrow(lat, lon):
    """
    Wrapper for column_row_from_lat_lon that converts column and row
    values to workable cell indices
    """
    col, row = column_row_from_lat_long(lat, lon, gpd_name='Nh50km')
    col = np.floor(col).astype(int)
    row = np.floor(row).astype(int)
    return col, row

def main(trajectory_file):
    """
    Converts trajectory coordinates in latitude, longitude to 
    column row and plots the grid with trajectory overlayed
    """

    # Get trajectory coordinates
    trajLatLon = read_yang_updated(trajectory_file)
    print (trajLatLon.head())
    lat = trajLatLon['Lat'].values
    lon = trajLatLon['Lon'].values
    
    # Convert trajectory to col, row indices grid
    col, row = latlon2colrow(lat, lon)
    icol = xr.DataArray(col, dims=['time'])
    irow = xr.DataArray(row, dims=['time'])
    
    # Set grid cells that intersect trajectory
    grid = makeGrid()
    grid[irow,icol] = 1
    
    # Plot grid and trajectory
    grid.plot()
    plt.show()
    
    
if __name__ == "__main__":
    trajectoryPath = '/home/apbarret/data/NPSNOW/yang_precip'
    trajectoryFile = 'yang_np_precip_updated_coords_31.csv'

    main( os.path.join(trajectoryPath, trajectoryFile) )
    
    
