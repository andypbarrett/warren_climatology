#----------------------------------------------------------------------
# Calculates daily accumulated precipitation from 6h data downloaded
# from RDA.  Daily netCDF files are written to directory structure
#----------------------------------------------------------------------

import xarray as xr
import datetime as dt
import pandas as pd
import glob
import os

import utilities.utilities as util

varNameIn = 'A_PCP_L1_Accum_1'
varNameOut = 'TOTPREC'

def _toDatetime(dt64):
    return pd.Timestamp(dt64.values).to_pydatetime()

def makeFilePathOut(time, varNameOut, diro):
    dateTime = _toDatetime(time)
    filo = 'CFSR.pgbh01.gdas.{:s}.{:s}.nc4'.format( varNameOut,
                                                    dateTime.strftime('%Y%m%d') )
    filePath = os.path.join(diro, dateTime.strftime('%Y'), dateTime.strftime('%m'), filo)
    return filePath

def write_to_netCDF(ds, diro='.', verbose=False):

    time = ds['time']
    
    filePath = makeFilePathOut(time, varNameOut, diro)
    if not os.path.exists( os.path.dirname(filePath) ):
        if verbose: print ( 'Making {:s}'.format(os.path.dirname(filePath)) )
        os.makedirs( os.path.dirname(filePath) )

    if verbose: print ( 'Writing data to {:s}'.format(filePath) )
    ds.to_netcdf(filePath)
    
    return

def process_one_file(f, diro='.', verbose=False):

    ds = xr.open_dataset(f)
    tp = util.sum6htoDay(ds[varNameIn])
    tp.name = varNameOut
    tp.attrs['units'] = 'mm'
    tp.attrs['product_description'] = 'daily accumulation'
    
    for time in tp['time']:
        write_to_netCDF(tp.sel(time=time), diro=diro, verbose=verbose)

    return

def cfsr_6htoDay(diri='.', diro='.', verbose=False):
    """
    Main routine
    """

    fileList = glob.glob( os.path.join(diri,'pgbh06.gdas.*.grb2.nc') )

    for f in fileList:

        if verbose: print ('Processing {:s}'.format(f))
        process_one_file(f, diro=diro, verbose=verbose)

    return

if __name__ == "__main__":
    diri = '/disks/arctic5_raid/abarrett/CFSR/archive/TOTPREC'
    diro = '/disks/arctic5_raid/abarrett/CFSR/TOTPREC'
    cfsr_6htoDay(diri=diri, diro=diro, verbose=True)

    
        
