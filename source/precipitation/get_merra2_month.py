# Gets MERRA2 variables
import datetime as dt
import numpy as np

def get_dataset(url):

    from pydap.client import open_url                                  
    from pydap.cas.urs import setup_session                            
    
    user = 'apbarret'
    pswd = 'T0talBollocks'
    
    session = setup_session(user, pswd, check_url=url)
    dataset = open_url(url, session=session)
    
    return dataset

def dataset_var_to_DataArray(dataset, varname, url=None,
                             level=[1000., 925., 850., 700., 500., 300.]):
    
    import xarray as xr
    import datetime as dt
    
    from collections import OrderedDict
    
    var = dataset[varname]
    time = dataset['time']
    lat  = dataset['lat']
    lon  = dataset['lon']

    print (var.ndim)
    
    if var.ndim > 3:
        print ('HERE')
        lev = dataset['lev']
        da = xr.DataArray(var[:], coords=[time[:],lev[:],lat[:],lon[:]],
                          dims=['time','lev','lat','lon'],
                          attrs=var.attributes, name=varname)
        da['lev'].attrs = OrderedDict([('long_name', lev.attributes['long_name']),
                                       ('units', lev.attributes['units'])])
        if level: da = da.sel(lev=level)
    else:
        da = xr.DataArray(var[:], coords=[time[:],lat[:],lon[:]],
                          dims=['time','lat','lon'],
                          attrs=var.attributes, name=varname)
    da['lat'].attrs = OrderedDict([('long_name', 'latitude'), ('units', 'degrees_north')])
    da['lon'].attrs = OrderedDict([('long_name', 'longitude'), ('units', 'degrees_east')])
    

    # To avoid conflicts between _FillValue and missing_value attributes when file is read
    da.attrs.pop('fmissing_value')
    da.attrs.pop('missing_value')

    if (np.array(da.shape) == 1).any(): da = da.squeeze(drop=True)

    ds = da.to_dataset()
    ds.attrs['created_by'] = 'Andrew P. Barrett <apbarret@nsidc.org'
    ds.attrs['created'] = dt.datetime.now().strftime('%Y%m%d')
    if url: ds.attrs['source'] = url
    
    return ds

def make_output_path(url, varName, root_diro='/disks/arctic5_raid/abarrett/MERRA2/monthly'):
    '''Generates a path for the output netCDF4 file'''
    import os
    import datetime as dt
    
    # Make filename
    tmp = os.path.basename(url).split('.')
    tmp.insert(2,varName) # insert varName in original filename

    # Extract date and create datetime object so year and month can be extracted
    #date = dt.datetime.strptime(tmp[3],'%Y%m%d')
    date = parse_date(tmp[3])
    
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
        print ('%write_to_netcdf4: Cannot create {:s}'.format(filo))
        
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

    odapdir = 'https://goldsmr4.gesdisc.eosdis.nasa.gov:443/opendap'
    
    with open(list_file) as f:
        lines = f.readlines()

    filenames = [l.strip() for l in lines]
    #for l in lines:
        #basename, datestr = re.search('(MERRA2_\d{3}\..+_.+_.+_.+\.(\d+).)', l).groups()
        #if len(datestr) == 6:
        #    date = dt.datetime.strptime(datestr, '%Y%m')
        #else:
        #    date = dt.datetime.strptime(datestr, '%Y%m%d')
        #filenames.append(os.path.join(odapdir, date.strftime('%Y'), date.strftime('%m'), basename+'nc4'))
    #    filenames.append( odapdir+l.strip() )
                         
    return filenames

def parse_date(datestr):
    if len(datestr) == 6:
        date = dt.datetime.strptime(datestr, '%Y%m')
    else:
        date = dt.datetime.strptime(datestr, '%Y%m%d')
    return date

def subset_urlList(urlList, begin, end):
    import datetime as dt
    import re
    import numpy as np

    if begin:
        dbeg = dt.datetime.strptime(begin, '%Y%m%d')
    else:
        dbeg = dt.datetime(1978,12,31)
    if end:
        dend = dt.datetime.strptime(end, '%Y%m%d')
    else:
        dend = dt.datetime.now()
    
    m = re.compile('\.(\d{6,8})\.')
    date = np.array([parse_date(m.search(f).groups()[0]) for f in urlList])

    dummy = np.array(urlList)

    return dummy[(date > dbeg) & (date <= dend)]
    
def main(listFile, varList=None, verbose=False, overwrite=False, begin=None, end=None, level=None):
    '''For a given MERRA2 dataset, extract variables (supplied as list) and write to
       to files using defined directory structure
    
    Args
    root dataset url
    list of variables
    '''
    
    # generate a url or list of urls OR date range
    urlList = get_urlList(listFile)

    # Subset urlList to files after 20100501
    urlList = subset_urlList(urlList, begin, end)

    # Loop through urls
    for url in urlList:
        
        # Get openDAP dataset
        if verbose: print ('   Getting {}'.format(url))
        dataset = get_dataset(url)

        # If varList is not set get all fields except lat, lon and time
        if not varList: varList = dataset.keys()[:-3]

        for varName in varList:

            if verbose: print ('   Extracting {} from dataset...'.format(varName))
            var = dataset_var_to_DataArray(dataset, varName, url=url)

            filo = make_output_path(url, varName)
            if verbose: print ('   Writing {} to {}'.format(varName,filo))
            write_to_netcdf4(var, filo)

    return
        
if __name__ == '__main__':

    import argparse

    parser = argparse.ArgumentParser(description='Downloads variables for files in listFile from NASA MERRA or MERRA2 reanalysis')
    parser.add_argument('listFile', metavar='listFile', type=str,
                        help='File containing list of URLs for files to download')
    parser.add_argument('varList', metavar='varList', type=str, nargs='+',
                        help='List of variable names to extract from downloaded files')
    parser.add_argument('--begin', '-b', type=str, action='store', default=None,
                        help='Data to begin extracting data')
    parser.add_argument('--end', '-e', type=str, action='store', default=None,
                        help='Data to end extracting data')
    parser.add_argument('--verbose', '-v', action='store_true')
    parser.add_argument('--overwrite', '-o', action='store_true',
                        help='Overwrite files on local drive')

    args = parser.parse_args()
    
    main(args.listFile, varList=args.varList, verbose=args.verbose, overwrite=args.overwrite, begin=args.begin, end=args.end)
