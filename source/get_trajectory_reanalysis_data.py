#----------------------------------------------------------------------
# Samples 3D grid precipitation stats along North Pole drifting
# station grids.
#
# 2018-10-4 A.P.Barrett <apbarret@nsidc.org>
#----------------------------------------------------------------------

import numpy as np
import xarray as xr
import pandas as pd
import datetime as dt
import os

from test_ungrid import lat_lon_to_col_row
from readers.reanalysis import read_precip_stats
from readers.npsnow import read_yang_updated

import matplotlib.pyplot as plt

def trajectory_to_indices(df):
    """
    Calculates column and row indices from lat and lon
    returning xarray DataArrays for use in extracting points
    """
    lat = df['Lat'].values
    lon = df['Lon'].values
    col, row = lat_lon_to_col_row(lat, lon)
    #col, row = column_row_from_lat_long(lat, lon, gpd_name='Nh50km')
    col = np.floor(col).astype(int)
    row = np.floor(row).astype(int)
    ix = xr.DataArray(row, dims=['time'])
    iy = xr.DataArray(col, dims=['time'])
    #it = xr.DataArray(df.index.values, dims=['time'])
    it = xr.DataArray(df.Date.values, dims=['time'])
    return it, ix, iy

def trajectory_filepath(id):
    dirpath = '/home/apbarret/data/NPSNOW/yang_precip'
    filepath = os.path.join(dirpath,'yang_np_precip_updated_coords_{:02d}.csv'.format(id))
    return filepath

def get_trajectories():
    """
    Gets trajectories in 1979 to 1991 period
    """
    np_stations = [22,24,25,26,28,29,30,31]
    trajectory = pd.concat([read_yang_updated( trajectory_filepath(id)) for id in np_stations])
#    trajectory.rename({'Unnamed: 0':'Date'}, axis=1, inplace=True)
    #trajectory = trajectory[trajectory.Date >= dt.datetime(1979,1,1)]
    trajectory.dropna(axis=0, how='any', inplace=True)
    trajectory.reset_index(drop=True, inplace=True)
    return trajectory

def scatter_plot(df, x, y, ax=None, xlabel='X', ylabel='Y', title=''):
    """
    Makes scatter plot of two columns in a dataframe with names x and y.

    Arguments
    ---------
    df - dataframe
    x - name of x column
    y - name of y column
    ax - axes object
    xlabel - label for x-axis
    ylabel - label for y-axis
    title - plot title
    """

    # Get upper limit for plot
    xmax = max(df[[x,y]].max().values)
    xmax = np.ceil(xmax/10.)*10.

    ax.plot(df[x], df[y], 'bo')
    ax.plot([0,xmax],[0,xmax], color='0.4')

    ax.set_xlim(0,xmax)
    ax.set_ylim(0,xmax)
    ax.set_aspect('equal','box')
    
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    ax.set_title(title)

    return

def main():

    # Read drifting station trajectory files - loop through them all
    print ('Getting NP data')
    trajectory = get_trajectories()
    
    # Calculate grid indices
    print ('Calculating trajectory indices')
    it, ix, iy = trajectory_to_indices(trajectory)

    # Loop through reanalyses
    for ir, reanalysis in enumerate(['ERAI','CFSR','MERRA','MERRA2','JRA55','ERA5']):
        
        # Read reanalysis precip stats data cube
        print ('Getting precip_stats for '+reanalysis)
        rdata = read_precip_stats(reanalysis)
        
        # Extract points
        print ('  Extracting points...')
        points = rdata['prectot'].sel(time=it, x=ix, y=iy, method='nearest')
        points = points.where(points.time.values == it.values)

        trajectory[reanalysis+'_prectot'] = points.values
        rdata.close()
        
        #if reanalysis == 'ERAI': break

    these_cols = ['Date','Lat','Lon','NP','Pg','Pc','ERAI_prectot','CFSR_prectot',
                  'MERRA_prectot','MERRA2_prectot','JRA55_prectot']
    trajectory.loc[:,these_cols].to_csv('np_reanalysis_month_comparison.csv')
    #exit()

    
if __name__ == "__main__":
    main()
    


