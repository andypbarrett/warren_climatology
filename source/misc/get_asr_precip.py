import xarray as xr
import pandas as pd

def read_netcdfs(fileList, varList, dim):
    def process_one_path(path, varList):
        with xr.open_dataset(path) as ds:
            ds.load()
            return ds[varList]
    
    datasets = [process_one_path(p, varList) for p in fileList]
    combined = xr.concat(datasets, dim)
    return combined

# Get list of files
url = 'https://rda.ucar.edu/thredds/dodsC/files/g/ds631.0/asr30fnl.fcst3.monthly/'
file_dates = pd.date_range('2000-01-01','2012-12-31',freq='M')
fileList = [url+'asr30km.fct.2D.'+d.strftime('%Y%m')+'.mon.nc' for d in file_dates]

combined = read_netcdfs(fileList, varList=['RAINNC', 'SNOWNC', 'XLAT', 'XLONG'], dim='time')

combined.to_netcdf('/disks/arctic5_raid/abarrett/ASR/asr30km.fct.2D.200001to201212.mon.nc')
#print combined['RAINNC'].min(), combined['RAINNC'].max()
#print combined['SNOWNC'].min(), combined['SNOWNC'].max()




