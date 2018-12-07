import pandas as pd
import numpy as np

from pinpoint.coord_converter import column_row_from_lat_long
from readers.reanalysis import read_precip_stats

x = """
1983-04-01   29.6  84.092500  217.540000  171.769826 169.365054
1979-12-01   32.5  84.422917  127.483819  189.561953 172.225426
1989-06-01   42.1  80.328333  174.471667  181.814154 158.423485
1983-03-01  103.0  84.132436  215.909359  172.120456 169.213822
1983-11-01   16.6  79.345889  175.754944  181.496682 156.218083
1989-01-01    6.0  77.003226  204.363441  167.883803 153.546683
1980-03-01   36.7  86.985076  128.659545  184.971136 175.573131
1990-05-01   24.3  83.401613  221.222043  170.111081 168.748095
1979-11-01   13.7  83.751667  132.754621  189.920972 170.346529
1980-07-01   16.4  88.531167   52.069917  182.319598 181.752546
"""


df = pd.DataFrame([ line.strip().split()[2:] for line in x.strip().split('\n') ],
                  columns=['Lat','Lon','iRow','iCol'])

col, row = column_row_from_lat_long(df['Lat'].values, df['Lon'].values, gpd_name='Nh50km')

df['oRow'] = col
df['oCol'] = row
print (df)
