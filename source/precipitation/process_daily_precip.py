# Calculates monthly precipitation statistics from daily data and
# writes to netCDF file
import utilities as util
import datetime as dt
import numpy as np

np.errstate(all='ignore') # to deal with Runtime warning about NaNs

def get_precip_statistics(fileGlob, reanalysis, threshold=1.):
    '''
    Generates a data set containing precipitation statistics for a given month
    
    reanalysis - name of renalaysis
    date - YYYYMM to get statistics
    
    Returns
    -------
    xarray Dataset
    '''

    import xarray as xr

    from constants import vnamedict
    varName = vnamedict[reanalysis]['PRECIP']['name']
    
    try:
        ds = util.read_month(fileGlob, reanalysis, 'PRECIP')
    except:
        print ( '% get_precip_statistics: Unable to open {}'.format(fileGlob) )
        raise
        
    wd_mean = util.wetday_mean(ds[varName], threshold=threshold)
    wd_freq = util.wetdays(ds[varName], threshold=threshold)
    wd_total = util.wetday_total(ds[varName], threshold=threshold)
    wd_max   = util.wetday_max(ds[varName], threshold=threshold)
    prectot = util.all_total(ds[varName])

    dsOut = xr.Dataset({'wetday_mean': wd_mean,
                     'wetday_frequency': wd_freq,
                     'wetday_total': wd_total,
                     'wetday_max': wd_max,
                     'prectot': prectot})
    if 'latitude' in ds: dsOut['latitude'] = ds['latitude']
    if 'longitude' in ds: dsOut['longitude'] = ds['longitude']
    
    return dsOut

def process_daily_precip(reanalysis, variable, start_date=None, end_date=None,
                         threshold=1., verbose=False, grid=None):
    '''Processes monthly precipitation statistics for a daterange'''

    if not start_date: start_date='19790101'
    if not end_date: end_date=dt.datetime.today().strftime('%Y%m%d')
    
    if verbose:
        print ( '% Processing {} from {} for {} to {}'.format(variable, reanalysis, start_date, end_date) )

    fileList = util.make_fileList(reanalysis, variable, (start_date, end_date), grid=grid)

    for f in fileList:

        if verbose:
            print ( '    Generating statistics for {}'.format(util.date_from_filename(f).strftime('%Y%m')) )

        try:
            ds = get_precip_statistics(f, reanalysis, threshold=threshold)
        except:
            pass # Not a good way to do this

        filo = util.make_outfile(f, reanalysis, variable, version='2')
        if verbose:
            print ( '    Writing statistics to {}'.format(filo) )
        ds.to_netcdf(filo)
    
    return

if __name__ == "__main__":

    import argparse

    parser = argparse.ArgumentParser(description='Estimates monthly statistics from daily reanalysis precipitation')
    parser.add_argument('reanalysis', metavar='reanalysis', type=str,
                        help='Name of reanalysis: CFSR, ERAI, MERRA, MERRA2, etc.')
    parser.add_argument('variable', metavar='variable', type=str,
                        help='Variable name')
    parser.add_argument('--start_date', '-sd', type=str, action='store', default=None,
                        help='Date to start processing (YYYYMMDD)')
    parser.add_argument('--end_date', '-ed', type=str, action='store', default=None,
                        help='Date to end processing (YYYYMMDD)')
    parser.add_argument('--threshold', '-t', type=float, action='store', default=1.,
                        help='Threshold for wetday')
    parser.add_argument('-v', '--verbose', action='store_true')
    parser.add_argument('--grid', '-g', type=str, action='store', default=None)
    
    args = parser.parse_args()
    
    process_daily_precip(args.reanalysis, args.variable,
                         start_date=args.start_date, end_date=args.end_date,
                         threshold=args.threshold, verbose=args.verbose, grid=args.grid)
    

    
                             
