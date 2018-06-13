# Gets MERRA2 variables

def get_dataset(url):

    from pydap.client import open_url                                  
    from pydap.cas.urs import setup_session                            
    
    user = 'apbarret'
    pswd = 'T0talBollocks'
    
    session = setup_session(user, pswd, check_url=url)
    dataset = open_url(url, session=session)
    
    return dataset

def get_var(dataset, varname):
    """
    Extracts a variable from a dataset and creates an xarray DataArray
    with coordinates and attributes

    dataset - a dataset returned by get_dataset
    varname - name of variable to extract

    returns: dataArray
    """
    
    import xarray as xr
    
    var = dataset[varname]
    time = dataset['TIME']
    lat  = dataset['YDim']
    lon  = dataset['XDim']

    da = xr.DataArray(var[:,:,:], coords=[time[:],lat[:],lon[:]], dims=['time','lat','lon'],
                      attrs=var.attributes, name=varname)
    
    da['time'].attrs = time.attributes
    da['lat'].attrs = lat.attributes
    da['lon'].attrs = lon.attributes

    # Set _FillValue for coordinate arrays
    da.lat.encoding['_FillValue'] = 9.969209968386869e+36
    da.lon.encoding['_FillValue'] = 9.969209968386869e+36

    # To avoid conflicts between _FillValue and missing_value attributes when file is read
    da.attrs.pop('fmissing_value')
    da.attrs.pop('missing_value')
    
    return da

def make_output_path(url, varName, root_diro='/disks/arctic5_raid/abarrett/MERRA/daily'):
    '''Generates a path for the output netCDF4 file'''
    import os
    import datetime as dt
    
    # Make filename
    tmp = os.path.basename(url).split('.')
    tmp.insert(2,varName) # insert varName in original filename

    # Extract date and create datetime object so year and month can be extracted
    date = dt.datetime.strptime(tmp[5],'%Y%m%d')
    
    return os.path.join(root_diro, varName, date.strftime('%Y'),
                        date.strftime('%m'), '.'.join(tmp)).replace('hdf','nc4')

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
        var.to_netcdf(filo) #, encoding={var.name: {'_FillValue': 9.96921e+36}}) 
			#	      'lat': {'_FillValue': 9.96909968386869e+36}, 
			#	      'lon': {'_FillValue': 9.96909968386869e+36}})
    except:
        print '%write_to_netcdf4: Cannot create {}'.format(filo)
        
    return

def get_urlList(list_file):
    '''
    Gets a list of url for the MERRA OpenDAP server

    This is a quick and dirty fix to the problem of querying the server for a list of 
    files for a given dataset.  For now, I generate the list using the Subsetter and
    extract file names from that list.
    '''
    import os
    import re
    from urlparse import urljoin
    import datetime as dt

    #odapdir = 'https://goldsmr2.gesdisc.eosdis.nasa.gov:443/opendap/MERRA/MAT1NXFLX.5.2.0'
    odapdir = 'https://goldsmr2.gesdisc.eosdis.nasa.gov:443/opendap'
    
    with open(list_file) as f:
        lines = f.readlines()

    filenames = [odapdir+l.strip() for l in lines]
    
    #filenames = []
    #for l in lines:
    #    basename, datestr = re.search('LABEL=(MERRA\d{3}.prod.assim.tavg1_2d_flx_Nx.(\d{8}).)SUB',l).groups()
    #    #basename, datestr = re.search('LABEL=(MERRA\d{3}.prod.assim.tavgM_2d_flx_Nx.(\d{6}).)SUB', l).groups()
    #    date = dt.datetime.strptime(datestr, '%Y%m%d')
    #    filenames.append(os.path.join(odapdir, date.strftime('%Y'), date.strftime('%m'),
    #                                  basename+'hdf')) #?PRECTOT[0:1:0][0:1:360][0:1:539],XDim[0:1:539],YDim[0:1:360],TIME[0]'))
    
    return filenames
    
def subset_urlList(urlList, start_date=None, end_date=None):
    import datetime as dt
    import re
    import numpy as np
    
    m = re.compile('\.(\d{8})\.')
    date = np.array([dt.datetime.strptime(m.search(f).groups()[0],'%Y%m%d') for f in urlList])

    if not start_date: start_date=date[0].stftime('%Y%m%d')
    if not end_date: end_date=date[:-1].strftime('%Y%m%d')
    
    dummy = np.array(urlList)

    return dummy[(date >= dt.datetime.strptime(start_date, '%Y%m%d')) &
                 (date <= dt.datetime.strptime(end_date, '%Y%m%d'))]
    
def hour2dayTot(daHr):
    '''
    Calculates total precipitation and carries attributes
    
    daHr - DataArray containing hourly data
    
    Returns: DataArray with daily total
    '''
    
    # Check if hourly values are rate or a total
    if (daHr.attrs['units'] == 'kg m-2 s-1') | (daHr.attrs['units'] == 'kg/m2/s'):
        daDay = daHr.sum(dim='time')*3600.
    else:
        daDay = daHr.sum(dim='time')
        
    daDay.attrs = daHr.attrs
    if (daHr.attrs['units'] == 'kg m-2 s-1') | (daHr.attrs['units'] == 'kg/m2/s'):
        daDay.attrs['units'] = 'mm'

    if 'begin_date' in daHr.time.attrs:
        daDay.attrs['time'] = str(daHr.time.attrs['begin_date'])
    
    return daDay

def hour2dayAvg(daHr):
    '''
    Calculates daily average from hourly values and carries attributes
    
    daHr - DataArray containing hourly data
    
    Returns: DataArray with daily total
    '''
    
    # Check if hourly values are rate or a total
    daDay = daHr.mean(dim='time')
        
    daDay.attrs = daHr.attrs

    if 'begin_date' in daHr.time.attrs:
        daDay.attrs['time'] = str(daHr.time.attrs['begin_date'])
    
    return daDay

def main(listFile, varList, verbose=False, overwrite=False, start_date=None, end_date=None):
    '''For a given MERRA dataset, extract variables (supplied as list) and write to
       to files using defined directory structure
    
    Args
    root dataset url
    list of variables
    '''

    # generate a url or list of urls OR date range
    urlList = get_urlList(listFile)

    # Subset urlList to files for start and end dates
    urlList = subset_urlList(urlList, start_date=start_date, end_date=end_date)
#    print urlList[0]
#    print urlList[-1]
#    return

    # Loop through urls
    for url in urlList:

        # Get openDAP dataset
        if verbose: print '% Getting {}'.format(url)
        dataset = get_dataset(url)

        # Loop through variables
        for varName in varList:
            
            if verbose: print '   Extracting daily {} from dataset...'.format(varName)
            var = get_var(dataset, varName)

            if any([varName == ii for ii in ['PRECTOT', 'PRECSNO']]):
                if verbose: print '   Integrating hourly values to daily totals'
                varDay = hour2dayTot(var)
            else:
                if verbose: print '   Averaging hourly values to daily means'
                varDay = hour2dayAvg(var)
            
            filo = make_output_path(url, varName)
            if verbose: print '   Writing {} to {}'.format(varName,filo)
            write_to_netcdf4(varDay, filo)

        #dataset.close()
        
        #if varDay.attrs['time'] == '19790131': break
        
if __name__ == '__main__':

    import argparse

    listFile = '/disks/arctic5_raid/abarrett/MERRA/daily/MERRA_MAT1NXFLX_filelist.txt'
    varList = ['PRECTOT', 'PRECSNO', 'FRSEAICE']    
    
    parser = argparse.ArgumentParser(description='Retrieves daily precipitation from MERRA')
    parser.add_argument('listFile', metavar='listfile', type=str,
                        help='List of opendap files')
    parser.add_argument('--variables', '-vr', type=str, nargs='+',
                        help='list of variables to process')
    parser.add_argument('--start_date', '-sd', type=str, action='store', default='19790101',
                        help='Date to start processing (YYYYMMDD)')
    parser.add_argument('--end_date', '-ed', type=str, action='store', default='20161231',
                        help='Date to end processing (YYYYMMDD)')
    parser.add_argument('-v', '--verbose', action='store_true')
    parser.add_argument('-o', '--overwrite', action='store_true')
    
    args = parser.parse_args()

    main(args.listFile, args.variables, verbose=args.verbose, overwrite=args.overwrite,
         start_date=args.start_date, end_date=args.end_date)
