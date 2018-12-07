#----------------------------------------------------------------------
# Module for reading gridded data using xarray
#----------------------------------------------------------------------

import xarray as xr

def read_geotiffs(fileList, concat_dim=None, sort_by_datetime=False):
    """Reads multiple geotiffs into a xarray DataArray"""
    def process_one_path(path):
        # Uses a context manager to ensure file is closed after use
        with xr.open_rasterio(path) as ds:
            ds.load()
            return ds

    if not concat_dim:
        concat_dim = 'dim0'

    if sort_by_datetime:
        # Currently, just sorts on filenames, assuming files sort on datetime
        paths = sorted(fileList)
    else:
        paths = fileList
        
    dataArrays = [process_one_path(p) for p in paths]
    combined = xr.concat(dataArrays, concat_dim)
    combined = combined.squeeze()
    return combined


