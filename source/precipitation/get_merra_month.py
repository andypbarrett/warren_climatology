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
    time = dataset['TIME']
    lat  = dataset['YDim']
    lon  = dataset['XDim']

    #print var.data
    #print var.attributes
    #print var.data.shape #[0,:,:]
    
#    da = xr.DataArray(var[:,:,:], coords=[time[:],lat[:],lon[:]], dims=['time','lat','lon'],
#                      attrs=var.attributes, name=varname)
    da = xr.DataArray(var.data, dims=['time','lat','lon']) #, coords=[lat.data[:],lon.data[:]], dims=['lat','lon'], attrs=var.attributes, name=varname)
    
    #da['time'].attrs = time.attributes
    #da['lat'].attrs = lat.attributes
    #da['lon'].attrs = lon.attributes

    # To avoid conflicts between _FillValue and missing_value attributes when file is read
    #da.attrs.pop('fmissing_value')
    #da.attrs.pop('missing_value')
    
    return da

def make_output_path(url, varName, root_diro='/disks/arctic5_raid/abarrett/MERRA/monthly'):
    '''Generates a path for the output netCDF4 file'''
    import os
    import datetime as dt
    
    # Make filename
    tmp = os.path.basename(url).split('.')
    tmp.insert(2,varName) # insert varName in original filename

    # Extract date and create datetime object so year and month can be extracted
    date = dt.datetime.strptime(tmp[3],'%Y%m')
    
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

    odapdir = 'https://goldsmr2.gesdisc.eosdis.nasa.gov:443/opendap/MERRA_MONTHLY/MATMNXFLX.5.2.0'
    
    with open(list_file) as f:
        lines = f.readlines()

    filenames = []
    for l in lines:
        basename, datestr = re.search('LABEL=(MERRA\d{3}.prod.assim.tavgM_2d_flx_Nx.(\d{6}).)SUB',l).groups()
        #basename, datestr = re.search('LABEL=(MERRA\d{3}.prod.assim.tavgM_2d_flx_Nx.(\d{6}).)SUB', l).groups()
        date = dt.datetime.strptime(datestr, '%Y%m')
        filenames.append(os.path.join(odapdir, date.strftime('%Y'), 
                                      basename+'hdf?PRECTOT[0:1:0][0:1:360][0:1:539],XDim[0:1:539],YDim[0:1:360],TIME[0]'))
    
    return filenames
    
def subset_urlList(urlList, varName):
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
    listFile = '/disks/arctic5_raid/abarrett/MERRA/monthly/wget_ztrcy6m6' #'/disks/arctic5_raid/abarrett/MERRA2/daily/M2T1NXFLX_V5.12.4_links_20171129_142234.txt'
    urlList = get_urlList(listFile)
    #varList = ['PRECTOT'] #, 'PRECTOTCORR'] urlList adds PRECTOT to openDAP call

    # HARDCODED #
    # Subset urlList to files after 20100501
    #urlList = subset_urlList(urlList, varList[0])
    
    # Loop through urls
    varName = 'PRECTOT'
    for url in urlList:

        # Get openDAP dataset
        if verbose: print '   Getting {}'.format(url)
        dataset = get_dataset(url)

        if verbose: print '   Extracting daily {} from dataset...'.format(varName)
        var = dataset_var_to_DataArray(dataset, varName)

        print var[0,0,0]
        break
    
        filo = make_output_path(url, varName)
        if verbose: print '   Writing {} to {}'.format(varName,filo)
        #write_to_netcdf4(var, filo)

        break
    
if __name__ == '__main__':
    main(verbose=True, overwrite=True)
