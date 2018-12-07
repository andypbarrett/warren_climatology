import numpy as np
import pandas as pd

def azimuthal_equal_area(lat, lon):
    """
    Returns x and y in meters for the azimuthal_equal_area grid

    Based on azimuthal_equal_area function of mapx
    
    Arguments
    ---------
    lat, lon geodetic coordinates in decimal degrees

    Returns
    -------
    x, y coordinates in meters
    """

    # Constants
    lat0, lon0 = 90.0, 0.0
    Rg = 6371228.

    phi = np.radians(lat)
    lam = np.radians(lon - lon0)

    rho = 2.*Rg * np.sin( (np.pi/4.) - (phi/2.) )
    x = rho * np.sin(lam)
    y = -1. * rho * np.cos(lam)

    return x, y

def forward_grid(x, y):

    r0, s0 = 179.75, 179.75
    scale = 50135.05

    r = r0 + (x/scale)
    s = s0 - (y/scale)

    return r, s

def lat_lon_to_col_row(lat, lon):

    x, y = azimuthal_equal_area(lat, lon)
    r, s = forward_grid(x, y)

    return r, s

def test_points():
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

    field = []
    for line in x.strip().split('\n'):
        field.append([ float(f) for f in line.strip().split()[2:] ])
    return pd.DataFrame(field,
                        columns=['Lat','Lon','iRow','iCol'])

def main():

    test_df = test_points()

    r, s = lat_lon_to_col_row(test_df['Lat'].values, test_df['Lon'].values)

    test_df['oRow'] = r
    test_df['oCol'] = s
    
    print (test_df)

if __name__ == "__main__":
    main()
    
