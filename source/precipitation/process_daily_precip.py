# Calculates monthly precipitation statistics from daily data and
# writes to netCDF file
import utilities as util

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

    try:
        data = util.read_month(fileGlob, reanalysis, 'PRECIP')
    except:
        print ( '% get_precip_statistics: Unable to open {}'.format(fileGlob) )
        
    wd_mean = util.wetday_mean(data, threshold=threshold)
    wd_freq = util.wetdays(data, threshold=threshold)
    wd_total = util.wetday_total(data, threshold=threshold)
    wd_max   = util.wetday_max(data, threshold=threshold)
    prectot = util.all_total(data)

    ds = xr.Dataset({'wetday_mean': wd_mean,
                     'wetday_frequency': wd_freq,
                     'wetday_total': wd_total,
                     'wetday_max': wd_max,
                     'prectot': prectot})

    return ds

def process_daily_precip(reanalysis, variable, start_date='19800101', end_date='20161231',
                         threshold=1., verbose=False):
    '''Processes monthly precipitation statistics for a daterange'''

    if verbose:
        print ( '% Processing {} from {} for {} to {}'.format(variable, reanalysis, start_date, end_date) )

    fileList = util.make_fileList(reanalysis, variable, (start_date, end_date))

    for f in fileList:

        if verbose:
            print ( '    Generating statistics for {}'.format(util.date_from_filename(f).strftime('%Y%m')) )
            
        ds = get_precip_statistics(f, reanalysis, threshold=threshold)

        filo = util.make_outfile(f, reanalysis, variable)
        if verbose:
            print ( '    Writing statistics to {}'.format(filo) )
        ds.to_netcdf(filo)
    
    return

if __name__ == "__main__":

    import argparse

    parser = argparse.ArgumentParser(description='Estimates monthly statistics from daily reanalysis precipitation')
    parser.add_argument('reanalysis', metavar='reanalysis', type=str,
                        help='Name of reanalysis: CFSR, ERA-Interim, MERRA, MERRA2, etc.')
    parser.add_argument('variable', metavar='variable', type=str,
                        help='Variable name')
    parser.add_argument('--start_date', '-sd', type=str, action='store', default='19800101',
                        help='Date to start processing (YYYYMMDD)')
    parser.add_argument('--end_date', '-ed', type=str, action='store', default='20161231',
                        help='Date to end processing (YYYYMMDD)')
    parser.add_argument('--threshold', '-t', type=float, action='store', default=1.,
                        help='Threshold for wetday')
    parser.add_argument('-v', '--verbose', action='store_true')
    
    args = parser.parse_args()
    
    process_daily_precip(args.reanalysis, args.variable,
                         start_date=args.start_date, end_date=args.end_date,
                         threshold=args.threshold, verbose=args.verbose)
    

    
                             
