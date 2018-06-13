
def filePath(reanalysis, date):
    '''
    Generates the file name for a PRECIP_STATS file for a given reanalysis
    
    reanalysis - name of reanalysis
    date - datetime object
    '''
    import os, glob
    from constants import filepath, vnamedict
    
    if (reanalysis == 'CFSR') & (date.year > 2010):
        path = os.path.join(filepath['CFSR2']['path'].format(vnamedict['CFSR2']['PRECIP']['name'],
                                                             date.year, date.month),
                            filepath['CFSR2']['ffmt'].format('PRECIP_STATS', date.strftime('%Y%m')))
    else:
        path = os.path.join(filepath[reanalysis]['path'].format(vnamedict[reanalysis]['PRECIP']['name'],
                                                                date.year, date.month),
                            filepath[reanalysis]['ffmt'].format('PRECIP_STATS', date.strftime('%Y%m')))
        
    if reanalysis == 'ERA-Interim': 
        path = path.replace('day','month')
    else:
        path = path.replace('??.nc','.month.nc')
    
    return path

