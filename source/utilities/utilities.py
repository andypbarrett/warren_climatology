import numpy as np

def daySum(x, input_freq_hours=6):
    """
    Calculates daily sums for days with complete number of timesteps
    for use with da.resample().apply()

    Arguments
    ---------
    x - input data
    input_freq_hour - frequency of input - assumes 6h
    """

    nexpect = int(24/6)

    sx = x.sum(dim='time', keep_attrs=True)
    if x.time.size != nexpect: sx[:] = np.nan
    return sx

def sum6htoDay(da):
    """
    Calculates daily sums from 6h reanalysis data.  Currently, the code
    assumes that 6h accumulations are for the 6h period preceding the
    datetime stamp; e.g. the precipitation total for 2018-01-01 06:00:00 is 
    is the accumulated precipitation for the 00:00:01 to 06:00:00 period.
    
    Arguments
    ---------
    da - xarray DataArray or DataSet object

    Returns
    -------
    a reduced object containing daily sums
    """
    return da.resample(time='24H', base=6, keep_attrs=True).apply(daySum)
    
