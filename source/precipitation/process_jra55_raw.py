# Processes JRA55 data downloaded from NCAR RDA into daily files and puts
# files into directory structures that are the same as other reanalysis
# products
#
# 2018-01-18 A.P.Barrett <apbarret@nsidc.org>

import os
import glob
import xarray as xr
import pandas as pd

vartable = {'PRECTOT': 'TPRAT_GDS4_SFC_ave3h',
            'PRECSNO': 'SRWEQ_GDS4_SFC_ave3h',
            'T2M': 'TMP_GDS4_HTGL'}
rawpath = {'PRECTOT': 'precip',
           'PRECSNO': 'precip',
           'T2M': 't2m'}
rawfile = {'PRECTOT': 'fcst_phy2m.061_tprat.reg_tl319',
           'PRECSNO': 'fcst_phy2m.064_srweq.reg_tl319',
           'T2M': 'anl_surf.011_tmp.reg_tl319'}

diri = '/disks/arctic5_raid/abarrett/JRA55'

def make_fileout(varName, time):
    """
    Makes name of output file
    """
    date = pd.to_datetime(time.data)
    return os.path.join(diri, varName,
                        str(date.year),
                        date.strftime('%m'),
                        rawfile[varName]+'.'+varName+'.'+ \
                        date.strftime('%Y%m%d')+'.nc4')
    #return 0

def write_to_netcdf(da, fileout):

    # Change coordinate names
    da_out = da.rename({'initial_time0_hours': 'time',
                        'g4_lat_2': 'lat',
                        'g4_lon_3': 'lon'})
        
    # Set fill values
    da_out.attrs['_FillValue'] = 9.96921e+36
    da_out.coords['lat'].attrs['_FillValue'] = 9.96921e+36
    da_out.coords['lon'].attrs['_FillValue'] = 9.96921e+36
    
    # Write to file
    directory = os.path.dirname(fileout)
    if not os.path.exists(directory):
        os.makedirs(directory)
    da_out.to_netcdf(fileout)

    return 0
    
def process_one_file(fili, varName, verbose=False):
    
    ds = xr.open_dataset(fili)
    da = ds[vartable[varName]]

    if varName == 'T2M':
        daysum = da.resample(initial_time0_hours='D').sum(
               dim='initial_time0_hours')
    else:
        daysum = da.resample(initial_time0_hours='D').sum(
               dim=['initial_time0_hours','forecast_time1'])
    daysum.attrs = da.attrs
    daysum = daysum.rename(varName)
    
    for time in daysum.coords['initial_time0_hours']:
        fileout = make_fileout(varName, time)
        if verbose:
            print( '   Writing data for {} to {}'.format(pd.to_datetime(time.data).strftime('%Y-%m-%d'),
                                                      fileout) ) 
        write_to_netcdf( daysum.sel(initial_time0_hours=time),
                         fileout )
    
    return

def get_fileList(varName):

    return glob.glob( os.path.join(diri, 'raw',
                                   rawpath[varName],
                                   rawfile[varName]+'.*.nc.gz') )

def process_jra55_raw(varName, verbose=False):

    if verbose: print('%process_jra55_raw: Getting file list...')
    fileList = get_fileList(varName)

    for f in fileList[1:]:
        if verbose: print( '   Processing {}'.format(f) )
        process_one_file(os.path.join(diri,f), varName, verbose=verbose)


if __name__ == "__main__":

    import argparse

    parser = argparse.ArgumentParser(description='Extracts and reformats JRA55 files downloaded from NCAR RDA')
    parser.add_argument('variable', metavar='variable', type=str,
                        help='Variable name: PRECTOT, PRECSNO, T2M')
    parser.add_argument('-v', '--verbose', action='store_true')
    
    args = parser.parse_args()


    process_jra55_raw(args.variable, verbose=args.verbose)
    
