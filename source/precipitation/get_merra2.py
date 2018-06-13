# Gets MERRA2 variables

def get_dataset(url):

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
        print '%write_to_netcdf4: Cannot create {}'.format(filo)
        
    return

def get_urlList(list_file):
    '''
    Gets a list of url for the MERRA2 OpenDAP server

    This is a quick and dirty fix to the problem of querying the server for a list of 
    files for a given dataset.  For now, I generate the list using the Subsetter and
    extract file names from that list.
    '''
    import os
    import re
    import datetime as dt

    odapdir = 'https://goldsmr4.gesdisc.eosdis.nasa.gov:443/opendap/MERRA2/M2T1NXFLX.5.12.4'
    
    with open(list_file) as f:
        lines = f.readlines()

    filenames = []
    for l in lines[1:]:
        basename, datestr = re.search('LABEL=(MERRA2_\d{3}.tavg1_2d_flx_Nx.(\d{8}).)SUB', l).groups()
        date = dt.datetime.strptime(datestr, '%Y%m%d')
        filenames.append(os.path.join(odapdir, date.strftime('%Y'), date.strftime('%m'), basename+'nc4'))
    
    return filenames
    
def subset_urlList(urlList):
    import datetime as dt
    import re
    import numpy as np
    
    m = re.compile('\.(\d{8})\.')
    date = np.array([dt.datetime.strptime(m.search(f).groups()[0],'%Y%m%d') for f in urlList])

    dummy = np.array(urlList)

    return dummy[date > dt.datetime(2010,5,1)]
    
def main(verbose=False, overwrite=False):
    '''For a given MERRA2 dataset, extract variables (supplied as list) and write to
       to files using defined directory structure
    
    Args
    root dataset url
    list of variables
    '''
    
    # generate a url or list of urls OR date range
    listFile = '/disks/arctic5_raid/abarrett/MERRA2/daily/M2T1NXFLX_V5.12.4_links_20171129_142234.txt'
    urlList = get_urlList(listFile)
    varList = ['PRECTOT'] #, 'PRECTOTCORR']

    # HARDCODED #
    # Subset urlList to files after 20100501
    urlList = subset_urlList(urlList)
    
    # Loop through urls
    for url in urlList:
        
        # Get openDAP dataset
        if verbose: print '   Getting {}'.format(url)
        dataset = get_dataset(url)
        
        for varName in varList:

            if verbose: print '   Extracting daily {} from dataset...'.format(varName)
            varHr = dataset_var_to_DataArray(dataset, varName)
            varDy = hour2day(varHr)

            filo = make_output_path(url, varName)
            if verbose: print '   Writing {} to {}'.format(varName,filo)
            write_to_netcdf4(varDy, filo)

if __name__ == '__main__':
    main(verbose=True, overwrite=True)
