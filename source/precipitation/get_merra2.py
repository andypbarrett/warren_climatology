# Gets MERRA2 variables

import merra2_utilities as m2util
import datetime as dt

def get_dataset_old(url):

    from pydap.client import open_url                                  
    from pydap.cas.urs import setup_session                            
    
    user = 'apbarret'
    pswd = 'T0talBollocks'
    
    session = setup_session(user, pswd, check_url=url)
    dataset = open_url(url, session=session)
    
    return dataset

def dataset_var_to_DataArray(dataset, varname):
    
    import xarray as xr
    
    var = dataset[varname]
    time = dataset['time']
    lat  = dataset['lat']
    lon  = dataset['lon']
    
    da = xr.DataArray(var[:,:,:], coords=[time[:],lat[:],lon[:]], dims=['time','lat','lon'],
                      attrs=var.attributes, name=varname)
    da['time'].attrs = time.attributes
    da['lat'].attrs = lat.attributes
    da['lon'].attrs = lon.attributes

    # To avoid conflicts between _FillValue and missing_value attributes when file is read
    da.attrs.pop('fmissing_value')
    da.attrs.pop('missing_value')
    
    return da

def hour2day(daHr):
    '''
    Calculates total precipitation and carries attributes
    
    daHr - DataArray containing hourly data
    
    Returns: DataArray with daily total
    '''
    
    # Check if hourly values are rate or a total
    if daHr.attrs['units'] == 'kg m-2 s-1':
        daDay = daHr.sum(dim='time')*3600.
    else:
        daDay = daHr.sum(dim='time')
        
    daDay.attrs = daHr.attrs
    if daHr.attrs['units'] == 'kg m-2 s-1':
        daDay.attrs['units'] = 'mm'

    if 'begin_date' in daHr.time.attrs:
        daDay.attrs['time'] = str(daHr.time.attrs['begin_date'])
    
    return daDay

def make_output_path(url, varName, root_diro='/disks/arctic5_raid/abarrett/MERRA2/daily'):
    '''Generates a path for the output netCDF4 file'''
    import os
    import datetime as dt
    
    # Make filename
    tmp = os.path.basename(url).split('.')
    tmp.insert(2,varName) # insert varName in original filename

    # Extract date and create datetime object so year and month can be extracted
    date = dt.datetime.strptime(tmp[3],'%Y%m%d')
    
    return os.path.join(root_diro, varName, date.strftime('%Y'),
                        date.strftime('%m'), '.'.join(tmp))

def write_to_netcdf4(var, filo):
    '''Writes xarray DataArray to netCDF4 file

    If output path does not exist, the path is created.
    Files are automatically overwritten

    var - xarray DataArray
    filo - string for output file path
    '''

    import os

    # Make directory, ignored if directory already exists
    if not os.path.isdir( os.path.dirname(filo) ):
        os.makedirs( os.path.dirname(filo) )

    try:
        var.to_netcdf(filo)
    except:
        print ('%write_to_netcdf4: Cannot create {:}'.format(filo))
        
    return

def main(listFile, varList, start_date=None, end_date=None, verbose=False, overwrite=False):
    '''For a given MERRA2 dataset, extract variables (supplied as list) and write to
       to files using defined directory structure
    
    Args
    root dataset url
    list of variables
    '''
    
    # generate a url or list of urls OR date range
    urlList = m2util.get_urlList(listFile)
    urlList = m2util.subset_urlList(urlList, start_date, end_date)

    # Loop through urls
    for url in urlList:
        
        # Get openDAP dataset
        if verbose: print ('   Getting {}'.format(url))
        dataset = m2util.get_dataset(url)
        
        for varName in varList:

            if verbose: print ( '   Extracting daily {} from dataset...'.format(varName) )
            #varHr = dataset_var_to_DataArray(dataset, varName)
            varHr = m2util.pydap2xarray(dataset, varName)
            varDy = m2util.hour2day(varHr)

            dsDy = varDy.to_dataset()
            dsDy.attrs['created_by'] = 'Andrew P. Barrett <apbarret@nsidc.org'
            dsDy.attrs['created'] = dt.datetime.now().strftime('%Y%m%d')
            if url: dsDy.attrs['source'] = url
    
            filo = make_output_path(url, varName)
            if verbose: print ( '   Writing {} to {}'.format(varName,filo) )
            write_to_netcdf4(dsDy, filo)

if __name__ == '__main__':

    import argparse

    parser = argparse.ArgumentParser(description='Downloads data files in listFile')
    parser.add_argument('listFile', type=str, help='File containing URLs for data')
    parser.add_argument('varList', type=str, nargs='+',
                        help='Variable or list of variables to extract')
    parser.add_argument('--start_date', '-sd', type=str, action='store', default=None,
                        help='Date of first file to download')
    parser.add_argument('--end_date', '-ed', type=str, action='store', default=None,
                        help='Date of last file to download')
    parser.add_argument('--verbose', '-v', action='store_true')
    parser.add_argument('--overwrite', action='store_false')

    args = parser.parse_args()

    main(args.listFile, args.varList, start_date=args.start_date, end_date=args.end_date,
         verbose=args.verbose, overwrite=args.overwrite)
