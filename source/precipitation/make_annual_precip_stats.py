#----------------------------------------------------------------------
# Generates annual precipitation statistics series
#
# 2018-07-06 A.P.Barrett
#----------------------------------------------------------------------
import glob
import re
import xarray as xr
import datetime as dt

def get_fileList(reanalysis, grid='Nh50km'):
    """
    Returns list of files containing monthly precipitation stats

    ***Currently returns files for Nh50km grid only***
    """
    
    globStr = {'ERAI': '/disks/arctic5_raid/abarrett/ERA_Interim/daily/PRECTOT/*/*/' + \
                       'era_interim.PRECIP_STATS.??????.month.Nh50km.nc',
               'CFSR': '/disks/arctic5_raid/abarrett/CFSR*/PRATE/*/*/' + \
                       'CFSR*.flxf06.gdas.PRECIP_STATS.??????.month.EASE_NH50km.nc',
               'MERRA': '/disks/arctic5_raid/abarrett/MERRA/daily/PRECTOT/*/*/' + \
                        'MERRA.prod.PRECIP_STATS.assim.tavg1_2d_flx_Nx.??????.month.Nh50km.nc4',
               'MERRA2': '/disks/arctic5_raid/abarrett/MERRA2/daily/PRECTOT/*/*/' + \
                         'MERRA2.tavg1_2d_flx_Nx.PRECIP_STATS.??????.month.Nh50km.nc4',
               'JRA55': '/projects/arctic_scientist_data/Reanalysis/JRA55/daily/TOTPREC/*/*/' + \
                        'JRA55.fcst_phy2m.PRECIP_STATS.??????.month.Nh50km.nc'}

    return glob.glob(globStr[reanalysis])

def fileOut(reanalysis):

    filo = {'ERAI': '/disks/arctic5_raid/abarrett/ERA_Interim/daily/PRECTOT/' + \
                       'era_interim.PRECIP_STATS.annual.Nh50km.nc',
               'CFSR': '/disks/arctic5_raid/abarrett/CFSR/PRATE/' + \
                       'CFSR.flxf06.gdas.PRECIP_STATS.annual.EASE_NH50km.nc',
               'MERRA': '/disks/arctic5_raid/abarrett/MERRA/daily/PRECTOT/' + \
                        'MERRA.prod.PRECIP_STATS.assim.tavg1_2d_flx_Nx.annual.Nh50km.nc4',
               'MERRA2': '/disks/arctic5_raid/abarrett/MERRA2/daily/PRECTOT/' + \
                         'MERRA2.tavg1_2d_flx_Nx.PRECIP_STATS.annual.Nh50km.nc4',
               'JRA55': '/projects/arctic_scientist_data/Reanalysis/JRA55/daily/TOTPREC/' + \
                        'JRA55.fcst_phy2m.PRECIP_STATS.annual.Nh50km.nc'}

    return filo[reanalysis]

def annual_precip_stats(reanalysis, verbose=False):

    fileList = get_fileList(reanalysis)
    fileList.sort()

    time = [dt.datetime.strptime(re.search('\d{6}',f).group(0),'%Y%m') for f in fileList]

    if verbose: print ('Getting data...')
    ds = xr.open_mfdataset(fileList, concat_dim='time')
    ds['time'] = time

    print (ds)
    
    if verbose: print ('Calculating annual summary...')
    dsAnn = xr.Dataset({'wetday_mean': ds['wetday_mean'].groupby('time.year').mean(dim='time'),
                        'wetday_frequency': ds['wetday_frequency'].groupby('time.year').sum(dim='time'),
                        'wetday_total': ds['wetday_total'].groupby('time.year').sum(dim='time'),
                        'wetday_max': ds['wetday_max'].groupby('time.year').mean(dim='time'),
                        'prectot': ds['prectot'].groupby('time.year').sum(dim='time')})

    if verbose: print ('Writing data to {:s}'.fileOut(reanalysis))
    dsAnn.to_netcdf(fileOut(reanalysis))

    return

if __name__ == "__main__":

    import argparse

    parser = argparse.ArgumentParser(description="Generates annual precipitation statistics series")
    parser.add_argument('reanalysis', type=str,
                        help='Reanalysis to process')
    parser.add_argument('--verbose', '-v', action='store_true')

    args = parser.parse_args()

    annual_precip_stats(args.reanalysis, verbose=args.verbose)
    
