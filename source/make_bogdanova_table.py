import numpy as np
import pandas as pd
import calendar

from merge_npsnow_data import get_station_list, get_precip

def month_sum(x):
    nday = calendar.monthrange(x.index[0].year, x.index[0].month)[1]
    if x.count() == nday:
        return x.sum()
    else:
        return np.nan

def make_table(verbose=False):

    stations = get_station_list()

    stat_dict = {}
    
    for sid in stations:

        if int(sid) > 4:    # Start with NP05
            if verbose: print ('Getting precipitation for '+sid)
            df = get_precip(sid)
            stat_dict['np'+sid] = df['amount'].resample('MS').apply(month_sum)

    table = pd.concat(stat_dict, axis=1, join='outer')

    return table
    
if __name__ == "__main__":
    table = make_table()

    # Get number of station months
    # Some years have more months than published
    nmonths = df[df.index >= '1956'].resample('A').count().sum(axis=1)
    
    print (table)
