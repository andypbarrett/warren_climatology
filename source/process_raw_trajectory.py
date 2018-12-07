# Reads original trajectory files for NPSNOW

import pandas as pd
import datetime as dt
import numpy as np

import dateutil
import pytz

# For reading and processing dates Times are Moscow (+3).  Moscow is now +2.5 I think

# Use datetime, dateutil and pytz
#E.g
#date = dateutil.parser.parse('19{:d}/{:02d}/{:02d} {:02d} +03:00'.format(73,10,4,10))
#date.astimezone(pytz.timezone('UTC'))
#Out[60]: datetime.datetime(1973, 10, 4, 7, 0, tzinfo=<UTC>)

#date
#Out[61]: datetime.datetime(1973, 10, 4, 10, 0, tzinfo=tzoffset(None, 10800))

def fieldtodate(y,m,d,h, utc=True):
    """
    Generates datetime object in UTC from year, month, date and hour
    Times in original files from AARI were for Moscow time (UTC+3).  However,
    prior to 2011, Moscow had summertime (UTC+4).  It is unclear from documentation
    if this was used at NP drifting stations.  I have chosen to assume all times in 
    original files, including during summer months are UTC+3.

    See: https://en.wikipedia.org/wiki/Moscow_Time
    """
    date = dateutil.parser.parse('19{:d}/{:02d}/{:02d} {:02d} +03:00'.format(y,m,d,h))
    if utc:
        return date.astimezone(pytz.utc)
    else:
        return date
    
def gendatetime(df):
    """Generates a list of datetime objects from DataFrame time stamps"""
    date = [fieldtodate(y,m,d,h) for y, m, d, h in zip(df['YY'], df['MM'], df['DD'], df['HH'])]
    return date

def parse_latlon(value):
    tenths, remainder = np.modf(value/10)
    fminute, degree = np.modf(remainder/100)
    return degree + (fminute*100 + tenths)/60.

def read_raw_trajectory(filepath):
    """Reads oroginal trajectory files"""
    df = pd.read_csv(filepath, skiprows=8, header=None,
                     names=['YY','MM','DD','HH','Lat','Lon'], sep='\s+')
    df['HH'].where(df['HH'] < 24, 0, inplace=True)
    df.index = gendatetime(df)

    df['Lat'] = df['Lat'].apply(parse_latlon)
    df['Lon'] = df['Lon'].apply(parse_latlon)

    
    return df.drop(['YY','MM','DD','HH'], axis=1)

if __name__ == "__main__":
    main()
    
