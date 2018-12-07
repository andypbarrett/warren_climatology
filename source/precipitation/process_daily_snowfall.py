# Calculates monthly precipitation statistics from daily data and
# writes to netCDF file
import utilities as util
import datetime as dt
import xarray as xr

def read_month(fileGlob, reanalysis, variable):
    """Work around to get monthly data"""
    ds = xr.open_mfdataset(fileGlob, concat_dim='time', data_vars='different')
    ds.set_coords(['latitude','longitude'], inplace=True)
    ds.coords['time'] = util.make_time_coordinate(fileGlob)
    ds.load()
    return ds

def get_month_snow(fileGlob, reanalysis, threshold=0.):
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
    varName = vnamedict[reanalysis]['SNOW']['name']
    
    try:
        #ds = util.read_month(fileGlob, reanalysis, 'SNOW')
        ds = read_month(fileGlob, reanalysis, 'SNOW')
    except:
        print ( '% get_month_snow: Unable to open {}'.format(fileGlob) )
        raise

    dsOut = xr.Dataset({'snow': ds['PRECSNO'].sum(dim='time', keep_attrs=True),
                        'snowday': ds['PRECSNO'].where(ds['PRECSNO'] > threshold).count(dim='time', keep_attrs=True)})
    dsOut = dsOut.where(dsOut.latitude > -999.)
    
    return dsOut

def process_daily_snow(reanalysis, variable, start_date=None, end_date=None,
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

        ds = get_month_snow(f, reanalysis, threshold=threshold)

        #try:
        #    ds = get_month_snow(f, reanalysis)
        #    print (ds)
        #except:
        #    pass # Not a good way to do this

        filo = util.make_outfile(f, reanalysis, variable)
        if verbose:
            print ( '    Writing statistics to {}'.format(filo) )
        ds.to_netcdf(filo)
    
    return

if __name__ == "__main__":

    import argparse

    parser = argparse.ArgumentParser(description='Estimates monthly total snowfall from daily reanalysis snowfall')
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
    
    process_daily_snow(args.reanalysis, args.variable,
                         start_date=args.start_date, end_date=args.end_date,
                         threshold=args.threshold, verbose=args.verbose, grid=args.grid)
    

    
                             
