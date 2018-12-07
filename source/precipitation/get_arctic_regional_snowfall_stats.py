import os
import glob
import re
import xarray as xr
import numpy as np
import pandas as pd

import datetime as dt

import utilities as util

region = {
    'CENTRAL_ARCTIC': 15,
    'BEAUFORT':       13,
    'CHUKCHI':        12,
    'BARENTS':         8,
    'KARA':            9,
    'LAPTEV':         10,
    'EAST_SIBERIAN':  11,
    'GREENLAND':       7,
    'BAFFIN':          6,
    'CAA':            14,
    'BERING':          3,
    'OKHOTSK':         2,
    'HUDSON_BAY':      4,
         }

def globFiles(reanalysis):
    """
    Returns list of PRECIP_STATS files for reanalysis
    """

    globPath = {
                'ERAI': '/disks/arctic5_raid/abarrett/ERA_Interim/daily/PRECTOT/'
                        '????/??/era_interim.PRECIP_STATS.??????.month.Nh50km.nc',
                'CFSR': '/disks/arctic5_raid/abarrett/CFSR*/TOTPREC/'
                        '????/??/CFSR*.*.PRECIP_STATS.??????.month.Nh50km.nc4',
                'MERRA': '/disks/arctic5_raid/abarrett/MERRA/daily/PRECTOT/'
                         '????/??/MERRA.prod.PRECIP_STATS.assim.tavg1_2d_flx_Nx.??????.month.Nh50km.nc4',
                'MERRA2': '/disks/arctic5_raid/abarrett/MERRA2/daily/PRECSNO/'
                          '????/??/MERRA2.tavg1_2d_flx_Nx.PRECSNO_STATS.??????.month.Nh50km.nc4',
                'JRA55': '/projects/arctic_scientist_data/Reanalysis/JRA55/daily/TOTPREC/'
                         '????/??/JRA55.fcst_phy2m.PRECIP_STATS.??????.month.Nh50km.nc',
               }

    fileList = glob.glob(globPath[reanalysis])

    #time = [util.date_from_filename(f) for f in fileList]
    
    return fileList 

def get_month_snowfall():
    """Calculates monthly mean snowfall and snowdays"""

    dirpath = '/disks/arctic5_raid/abarrett/MERRA2/daily/PRECSNO'
    fileGlob = glob.glob( os.path.join(dirpath,
                                       '????',
                                       '??',
                                       'MERRA2.tavg1_2d_flx_Nx.PRECSNO_STATS.??????.month.Nh50km.nc4') )

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
                                       'MERRA2.tavg1_2d_flx_Nx.PRECIP_STATS.??????.month.Nh50km.v2.nc4') )

    p = re.compile('\.(\d{6})\.month')
    
    ds = xr.open_mfdataset(sorted(fileGlob), concat_dim='time') #, data_vars='different')
    time = [dt.datetime.strptime(p.search(f).groups(1)[0],'%Y%m') for f in sorted(fileGlob)]
    ds.coords['time'] = time

    return ds

def read_precip_stats(reanalysis):
    """
    Reads monthly precip_stats files into a big data cube for a given reanalysis.

    NB I use sortby to ensure that data are returned in time order.

    Returns: a xarray dataset
    """
    fileList = globFiles(reanalysis)
    ds = xr.open_mfdataset(fileList, concat_dim='time', 
                           data_vars=['wetday_mean',
                                      'wetday_frequency',
                                      'wetday_total',
                                      'wetday_max',
                                      'prectot',])
    ds.coords['time'] = [util.date_from_filename(f) for f in fileList]
    
    return ds.sortby(ds.time)

def read_region_mask():
    """
    Reads the Nh50km Arctic region mask and puts it into a xarray DataArray compatable with
    the precip_stats Dataset
    """

    mask_path = ('/oldhome/apbarret/data/seaice_indices/'
                 'Arctic_region_mask_Meier_AnnGlaciol2007_Nh50km.dat')
    nrow = 360
    ncol = 360
    
    result = xr.DataArray(np.fromfile(mask_path, dtype=float).reshape(nrow,ncol),
                          dims=['x','y'])
    return result

def _get_region_stats(ds, mask, region_name):
    agg = ds.where(mask == region[region_name]).mean(dim=['x','y'])
    return agg #agg.drop(['latitude','longitude'])

def arctic_regional_precip_stats(reanalysis, verbose=False, timespan='month'):
    """
    Calculates regional precip stats for a reanalysis
    """

    if verbose: print ('   Getting precip stats fields...')
    precip_stats = get_month_prectot()
    prectot = precip_stats['prectot']

    if verbose: print ('   Getting snowfall stats...')
    snow_stats = get_month_snowfall()
    snowfall = snow_stats['snow']

    if timespan == 'annual':
        prectot = prectot.groupby('time.year').sum(dim='time')
        snowfall = snowfall.groupby('time.year').sum(dim='time')
        
    snow_fraction = snowfall / prectot
    
    if verbose: print ('   Getting mask...')
    mask = read_region_mask()

    by_region = []
    for key in region.keys():
        if verbose: print ('   Getting regional stats for '+key+'...')
        by_region.append( _get_region_stats(snow_fraction, mask, key).to_dataframe(name=key) )

    precip_stats.close()
    snow_stats.close()
    
    #by_region = [_get_region_stats(ds, mask, key).to_dataframe() for key in region.keys()]

    if verbose: print ('   Concatenating dataframes...')
    df = pd.concat( by_region, axis=1, keys=(region.keys()) )
    
    return df 

def read_arctic_regional_stats(filepath):
    """
    Reads a summary file of Arctic regional stats into a multi-level pandas data frame
    """
    return pd.read_csv(filepath, header=[0,1], index_col=0,
                       infer_datetime_format=True, parse_dates=True)
    
def get_arctic_regional_stats(verbose=False, timespan='month'):
    """
    Calculates stats for all reanalyses

    Just runs for MERRA2 at the moment
    """
    
    #products = [
    #            'ERAI',
    #            'CFSR',
    #            'MERRA',
    #            'MERRA2',
    #            'JRA55',
    #            ]
    products = ['MERRA2']
    
    for reanalysis in products:
        
        if verbose: print ('Getting stats for '+reanalysis)
        df = arctic_regional_precip_stats(reanalysis, verbose=verbose, timespan=timespan)

        if timespan == 'annual':
            outfile = '{:s}_regional_snowfall_fraction.annual.v2.csv'.format(reanalysis.lower())
        else:
            outfile = '{:s}_regional_snowfall_fraction.month.v2.csv'.format(reanalysis.lower())
            
        if verbose: print ('   Writing to '+outfile)
        df.to_csv(outfile)

if __name__ == "__main__":
    get_arctic_regional_stats(verbose=True, timespan='annual')
    
    


