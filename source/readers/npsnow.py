#----------------------------------------------------------------------
# A module of readers for ascii data files containing data from the
# North Pole Drifting Stations
#----------------------------------------------------------------------
import pandas as pd
import datetime as dt
import calendar
import numpy as np

def read_precip(fili):
    """
    Reader for precipitation files contained in the NPSNOW data set

    In NPSNOW precip files, dry-days have amount=-9.9 and type=-9.
    These are set to 0.0 and 0 respectively.  This dry-days are distinct
    from days with trace precipitation, which have amount 0.0 and non-zero 
    type.

    Arguments
    ---------
    fili - file path

    Returns
    -------
    Pandas dataframe containg precipitation data for one station
    """

    df = pd.read_csv(fili, header=None, delim_whitespace=True,
                     #na_values={'amount': -9.9, 'type': -9}, 
                     names=['statid','month','day','year','amount','type'])

    isday = [row[1]['day'] <= \
             calendar.monthrange( int(row[1]['year']),int(row[1]['month']) )[1] \
             for row in df.iterrows()]
    df = df[isday] # only return rows with valid date

    df.index = [dt.datetime(int(row[1]['year']),
                            int(row[1]['month']),
                            int(row[1]['day']) ) \
                for row in df.iterrows()] # Reset index to date

    # Assumes zero precipitation/dry days are marked as -9.9, set to zero
    df = df.where(df > 0., 0.0)
    
    return df[['statid','amount','type']]

def read_position(fili):
    """
    Reader for position files contained in the NPSNOW dataset

    Arguments
    ---------
    fili - file path

    Returns
    -------
    Pandas dataframe containing drifting station positions
    """

    df = pd.read_csv(fili, header=None, delim_whitespace=True,
                     names=['year','month','day','hour','lat','lon'])
    df['hour'][df['hour'] == 24] = 0 #There is no hour 24
    if (df['hour'] > 24).any():
        df['hour'][df['hour'] > 24] = 12

    # This is a fix to deal with non-valid dates: e.g. 30 February
    isday = [row[1]['day'] <= \
             calendar.monthrange( int(row[1]['year']),int(row[1]['month']) )[1] \
             for row in df.iterrows()]
    df = df[isday] # only return rows with valid date

    df.index = [dt.datetime(int( '19{:2d}'.format(row[1]['year']) ),
                            int(row[1]['month']),
                            int(row[1]['day']),
                            int(row[1]['hour'])) \
                for row in df.iterrows()]
    df['lat'] = df['lat'].floordiv(1000).astype(float) + \
                df['lat'].mod(1000).divide(600)
    df['lon'] = df['lon'].floordiv(1000).astype(float) + \
                df['lon'].mod(1000).divide(600)
    
    return df[['lat','lon']]

def read_uniformat(fili):
    """
    Reads unformat files from US Russian joint Atlases
    
    Argument
    --------
    fili - file path

    Returns
    -------
    Pandas data frame
    """
    import numpy as np
    
    df = pd.read_csv(fili, header=None, delim_whitespace=True,
                     names=['WMO-ID','year','month','day','time','pos_flag',
                            'lat','lon','tair','slp','wdir','wspd','total_cloud',
                            'low_cloud','rh','tdew','twet','vap','precip','tsurf',
                            'sst','name'],
                     na_values={'pos_flag': 9, 'lat': 99.99, 'lon': 999.99,
                                'tair': 999.99, 'slp': 9999.9, 'wdir': 999.9,
                                'wspd': 999.9, 'total_cloud': 99.9, 'low_cloud': 99.9,
                                'rh': 999.9, 'tdew': 999.99, 'vap': 9999.9,
                                'precip': -1.00, 'tsurf': 999.99, 'sst': 999.99})

    df.index = [dt.datetime( int(row[1]['year']),
                             int(row[1]['month']),
                             int(row[1]['day']),
                             int(row[1]['time']//100),
                             np.mod( int(row[1]['time']), 100) ) for row in df.iterrows() ]

    return df.drop(['year','month','day','time'], axis=1)

def read_snowstake(fili):
    """
    Reads the snow stake file from the NPSNOW data set
    """
    def parse_line(l):
        field = l.split()
        statid = int( field[0] )
        year = 1900 + int( field[1] )
        month = int( field[2] )
        nday = calendar.monthrange(year, month)[1]

        df = pd.DataFrame( {'snowdepth': [float(s) for s in field[3:3+nday]],
                              'station': [statid for s in field[3:3+nday]]},
                             index=pd.date_range( '{:4d}/{:d}/1'.format(year,month),
                                                  periods=nday, freq='D' ) )
        df[df >= 666] = np.nan
        
        return df 
        
    f = open(fili, 'r')
    df = pd.concat( [parse_line(l) for l in f.readlines()] )
    f.close()
    
    return df

def dateparser(x):
    return dt.datetime.strptime('19{:s}'.format(x),'%Y %m %d')

def datetimeparser(x):
    #print ('*19{:s}*'.format(x))
    #return None
    return dt.datetime.strptime('19{:s}'.format(x),'%Y %m %d %H')

def read_met(fili):
    """
    Reads meteorological data files.  These contain wind speed and
    wind direction.
    """

    names = ['Station_ID',
             'Year',
             'Month',
             'Day',
             'Time',
             'Latitude',
             'Longitude',
             'TAIR',
             'RH',
             'SLP',
             'WDIR',
             'WSPD',
             'TOTCLD',
             'LOWCLD',
             'TSURF',]
    
    df = pd.read_csv(fili, sep='\s+', header=None, names=names, na_values=[9999, 9999.0],
                     parse_dates={'date': ['Year','Month','Day','Time']}, index_col='date',
                     date_parser=datetimeparser)
    return df
    
    
def read_combined(fili):
    """
    Reads a combined file of drifting station observations
    """

    names = ['Station_ID',
             'Year',
             'Month',
             'Day',
             'Latitude',
             'Longitude',
             'TAIR',
             'RH',
             'SLP',
             'UWIND',
             'VWIND',
             'TOTCLD',
             'LOWCLD',
             'TSURF',
             'KDIFF',
             'KDIR',
             'KGLOBAL',
             'KREF',
             'ALBEDO',
             'QNET',
             'PRECTOT',
             'PTYPE',
             'SNODEP_AVG',
             'SNODEN_AVG',
             'SNOLIQ_AVG',
             'SNODEP_STK',]
    names.extend(['SNODEN{:02d}'.format(i) for i in range(1,11)])
    names.extend(['SNOLIQ{:02d}'.format(i) for i in range(1,11)])
    names.extend(['SNODEP{:03d}'.format(i) for i in range(1,101)])

    df = pd.read_csv(fili, header=None, names=names, sep='\s+', na_values=9999.0,
                     parse_dates={'date': ['Year','Month','Day']}, index_col='date',
                     date_parser=dateparser)

    return df

def plot_trajectory(df):
    """
    Dummy routine for plotting drifting station trajectory
    """
    coords = ll2xy( df, map_proj)
    xy = pd.DataFrame({'x': coords[:,0], 'y': coords[:,1]}, index=df.index)
    xyMon = xy.resample('M').mean()
    ax = plt.subplot(projection=map_proj)
    ax.add_feature(cfeature.LAND)
    ax.plot(coords[:,0], coords[:,1])
    ax.plot(xyMon['x'].values, xyMon['y'].values, 'ro')
    plt.show()

def read_yang(fili):
    """
    Reads Excel file containing Yang corrected monthly precipitation
    
    Arguments
    ---------
    fili - file path
    
    Returns
    -------
    Pandas dataframe containing monthly precipitation
    """
    df = pd.read_excel(fili, sheet_name='monthly-all', header=0, skiprows=[1,2,3], 
                   na_values='-', usecols=14)
    df = df.dropna(how='all')
    return df

def read_yang_updated(fili):
    """
    Reads csv file containing Yang precipitation with updated coordinates

    Arguments
    ---------
    fili - file path

    Returns
    -------
    Pandas data frame containing monthly precipitation
    """
    df = pd.read_csv(fili, header=0, parse_dates=True)
    df.rename({'Unnamed: 0':'Date'}, axis=1, inplace=True)
    df['Date'] = [dt.datetime.strptime(t,'%Y-%m-%d') for t in df.Date.values]
    return df




    

    
