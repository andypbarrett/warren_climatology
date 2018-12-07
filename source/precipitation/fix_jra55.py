#----------------------------------------------------------------------
# Fixes JRA55 TOTPREC.  Original processing summed 3h TOTPREC and
# SNOFALL to get daily values.  However, units are mm/day.  Values
# need to be averaged instead.  This code multiplies fields by 0.125 (3/24)
# to get correct precipitation and snow fall totals.
#
# ******OLD FILES ARE WRITTEN TO copy/variable/ ******
#----------------------------------------------------------------------
import xarray as xr
import os, glob
import shutil

diri = '/projects/arctic_scientist_data/Reanalysis/JRA55/daily'

def get_fileList(variable, grid=None):
    """
    Gets a list of files for TOTPREC or SNOFALL
    """
    if grid:
        gridstr = '.{:s}'.format(grid)
    else:
        gridstr = ''
    return glob.glob( os.path.join( diri, variable,
                                    '*/*/JRA55.fcst_phy2m.TOTPREC.????????{:s}.nc'.format(gridstr) ) )
def fixit(f, variable):
    """
    Does rescaling of variable
    """
    ds = xr.open_dataset(f)
    ds2 = ds.copy()
    ds.close()
    
    ds2[variable].values = ds2[variable].values * 0.125
    ds2.to_netcdf(f, mode='w', engine='scipy')
    return

def fix_jra55(variable, grid=None, verbose=False):

    fileList = get_fileList(variable, grid=grid)

    # Make directory to copy old files
    copyDir = os.path.join(diri,'copy',variable)
    if not os.path.exists(copyDir):
        if verbose: print ('Creating {:s}'.format(copyDir))
        os.makedirs( copyDir )

    for f in fileList:

        # Copy file
        fcpy = os.path.join(copyDir, os.path.basename(f).replace('.nc','.old.nc'))
        if os.path.exists(fcpy):
            print ('....Skipping {:s}'.format(f))
            continue # Skip files that have already been corrected

        if verbose: print ('  Copying {:s} to {:s}'.format(f, fcpy))
        shutil.copy2( f, fcpy )

        # Fix variable
        if verbose: print ('  Fixing {:s}'.format(variable) )
        fixit(f, variable)
        break
    
    return

if __name__ == "__main__":

    import argparse

    parser = argparse.ArgumentParser(description='Rescales JRA55 TOTPREC or SNOFALL to fix error')
    parser.add_argument('variable', type=str, help='Name of variable to process')
    parser.add_argument('--grid', '-g', default=None,
                        help='Select grid to rescale: e.g. Nh50km')
    parser.add_argument('--verbose', '-v', action='store_true')
    args = parser.parse_args()

    fix_jra55(args.variable, grid=args.grid, verbose=args.verbose)
    
