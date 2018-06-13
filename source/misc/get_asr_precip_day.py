import xarray as xr
import pandas as pd
import matplotlib.pyplot as plt
import calendar

def read_netcdfs(fileList, dim):
    def process_one_path(path):
        with xr.open_dataset(path) as ds:
            ds.load()
            return ds['RAINNC'].sum(dim='Time')
    
    datasets = [process_one_path(p) for p in fileList]
    combined = xr.concat(datasets, dim)
    return combined

# Get list of files
url = 'https://rda.ucar.edu/thredds/dodsC/files/g/ds631.0/asr30fnl.fcst3.2D/'

month_list = pd.date_range('2000-01-01 00:00:00','2012-12-31 23:59:59',freq='M')

for date in month_list:

    dinm = calendar.monthrange(date.year, date.month)[1]

    start_date = '{:7s}-{:02d} 00:00:00'.format(date.strftime('%Y-%m'), 1)
    end_date = '{:7s}-{:02d} 23:59:59'.format(date.strftime('%Y-%m'), dinm)

    filo = '/disks/arctic5_raid/abarrett/ASR/asr30km.fct.2D.{:6s}.month.nc'.format(date.strftime('%Y%m'))

    file_dates = pd.date_range(start_date,end_date,freq='D')
    fileList = [url+'asr30km.fct.2D.'+d.strftime('%Y%m%d')+'.nc' for d in file_dates]

    # get lat and lon
    ds = xr.open_dataset(fileList[0])
    xlat = ds['XLAT']
    xlong = ds['XLONG']

    combined = read_netcdfs(fileList, dim='Time')
    monthTotal = combined.sum(dim='Time')

    print '% Writing monthly total for {:7s} to {:s}'.format(date.strftime('%Y-%m'), filo)
    monthTotal.to_netcdf(filo)




