# Summarizes PRECIP_STATS to accumulation period totals for Arctic region and a grids

import xarray as xr
import numpy as np

def fileGlob(reanalysis):
    '''
    Generates a file glob for PRECIP_STATS
    '''
    
    import os, glob
    from constants import filepath

    globDict = {'CFSR': '/disks/arctic5_raid/abarrett/CFSR/PRATE/*/*/CFSR*.*.PRECIP_STATS.*.nc',
                'CFSR2': '/disks/arctic5_raid/abarrett/CFSR2/PRATE/*/*/CFSR2.*.PRECIP_STATS.*.nc',
                'MERRA': '/disks/arctic6_raid/MERRA/daily/PRECTOT/*/*/MERRA.prod.assim.tavg1_2d_lnd_Nx.PRECIP_STATS.*.month.nc',
                'ERA-Interim': '/disks/arctic5_raid/abarrett/ERA_Interim/daily/PRECTOT/*/era_interim.PRECIP_STATS.*.month.nc',
                'JRA55': '/disks/arctic5_raid/abarrett/JRA55/PRECTOT/*/*/fcst_phy2m.061_tprat.reg_tl319.PRECIP_STATS.*.month.nc4'}
    return globDict[reanalysis]

def filePath(reanalysis, date):
    '''
    Generates the file name for a PRECIP_STATS file for a given reanalysis
    
    reanalysis - name of reanalysis
    date - datetime object
    '''
    import os, glob
    from constants import filepath, vnamedict
    
    if (reanalysis == 'CFSR') & (date.year > 2010):
        path = os.path.join(filepath['CFSR2']['path'].format(vnamedict['CFSR2']['PRECIP']['name'],
                                                             date.year, date.month),
                            filepath['CFSR2']['ffmt'].format('PRECIP_STATS', date.strftime('%Y%m')))
    else:
        path = os.path.join(filepath[reanalysis]['path'].format(vnamedict[reanalysis]['PRECIP']['name'],
                                                                date.year, date.month),
                            filepath[reanalysis]['ffmt'].format('PRECIP_STATS', date.strftime('%Y%m')))
        
    if reanalysis == 'ERA-Interim': 
        path = path.replace('day','month')
    else:
        path = path.replace('??.nc','.month.nc')

    if reanalysis == 'MERRA': path = path.replace('MERRA???','MERRA')
    
    return path

def make_fileList(reanalysis, year):
    '''
    Generates a list of files containing monthly statistics for the accumulation period

    reanalysis - name of reanalysis
    year - year to calculate (refers to year of the end of acc. period
    '''
    import pandas as pd
    import datetime as dt
    
    start = dt.datetime(year-1,8,1)
    end = dt.datetime(year,4,30)
    date = pd.date_range(start, end, freq='M')
    
    return [filePath(reanalysis, d) for d in date], date

def daysinmonth(date):
    import calendar
    
    days = [calendar.monthrange(d.year, d.month)[1] for d in date]
    return xr.DataArray(days, coords=[date], dims=['time'])

def read_one_era_interim(fileName, date):
    '''
    A special function to read ERA-Interim files and swap
    names but not values of lat and lon for file before 2016
    '''
    with xr.open_dataset(fileName) as ds:
        if date.year < 2016:
            ds.rename({'lat': 'lonx', 'lon': 'latx'}, inplace=True)
            ds.rename({'latx': 'lat', 'lonx': 'lon'}, inplace=True)
        ds.load()
    return ds

def read_one_reanalysis(fileName):
    with xr.open_dataset(fileName) as ds:
        ds.load()
    return ds

def read_files_in_list(fileList, date, reanalysis):
    '''
    Reads file from a list according to reanalysis
    '''
    if reanalysis == 'ERA-Interim':
        datasets = [read_one_era_interim(f, d) for f, d in zip(fileList, date)]
    else:
        datasets = [read_one_reanalysis(f) for f in fileList]

    ds = xr.concat(datasets, 'time')
    ds.coords['time'] = date

    return ds

def process_one_period(reanalysis, year, verbose=False):
    '''
    Calculate statistics for a single winter accumulation period
    '''
    import os
    
    fileList, date = make_fileList(reanalysis, year)
    if any([not os.path.exists(f) for f in fileList]):
        print ('%process_one_period: one or more files do not exist')
        return -1
    
    if verbose: print ('     Processing data for {}'.format(year))
         
    ds = read_files_in_list(fileList, date, reanalysis)

    # Sum totals
    precTot = ds['prectot'].sum(dim='time')
    wetdayTot = ds['wetday_total'].sum(dim='time')

    # Calculate wetday count and wetday frequency
    ndays = daysinmonth(date)
    nwetdays = (ds['wetday_frequency']*ndays).sum(dim='time') #( / ndays.sum(dim='time')
    fwetdays = nwetdays / ndays.sum(dim='time')

    # Calculate mean precip on wetdays
    wetdayAve = wetdayTot.where(wetdayTot > 0.) / nwetdays
    
    newDs = xr.Dataset({'precTot': precTot,
                        'wetdayTot': wetdayTot,
                        'nwetdays': nwetdays,
                        'fwetdays': fwetdays,
                        'wetdayAve': wetdayAve})

    ds.close()

    return newDs

def make_outfile(reanalysis):
    from constants import filepath, vnamedict
    import os
    if reanalysis == 'ERA-Interim':
        diro = '/'.join(filepath[reanalysis]['path'].split('/')[:-1]).format(vnamedict[reanalysis]['PRECIP']['name'])
        filo = filepath[reanalysis]['ffmt'].format('PRECIP_STATS','x').replace('x.day','accumulation.annual')
    else:
        diro = '/'.join(filepath[reanalysis]['path'].split('/')[:-2]).format(vnamedict[reanalysis]['PRECIP']['name'])
        filo = filepath[reanalysis]['ffmt'].format('PRECIP_STATS','x').replace('x??','accumulation.annual')
    return os.path.join(diro,filo)

def process_precip_stats(reanalysis, start_year=1981, end_year=2017, verbose=False):
    import datetime as dt

    #ybeg = 1981
    #yend = 1985 #2016

    if verbose: print ('%  Processing {} PRECIP_STATS for {:d} to {:d}'.format(reanalysis, start_year, end_year))
    year = np.arange(start_year,end_year)
    ds = xr.concat([process_one_period(reanalysis, y, verbose=verbose) for y in year], 'time')
    ds.coords['time'] = [dt.datetime(y,1,1) for y in year]
    
    filo = make_outfile(reanalysis)
    if verbose: print ('%  writing {} PRECIP_STATS to {}'.format(reanalysis, filo))
    ds.to_netcdf(filo)
    
    return


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description='Summarizes monthly precipitation statistics from renalysis')
    parser.add_argument('reanalysis', metavar='reanalysis', type=str,
                        help='Name of reanalysis: CFSR, ERA-Interim, MERRA, MERRA2, etc.')
    parser.add_argument('--start_year', metavar='start_year', type=int, default=1981,
                        help='Year to start analysis')
    parser.add_argument('--end_year', metavar='end_year', type=int, default=2017,
                        help='Year to end analysis')
    parser.add_argument('-v', '--verbose', action='store_true')
    args = parser.parse_args()

    process_precip_stats(args.reanalysis, start_year=args.start_year, end_year=args.end_year, verbose=args.verbose)
    

