import numpy as np

def nh_latlon2colrow(lat, lon):
    """
    Calculates grid column and row from latitude and
    longitude coordinates
    """

    R = 6371.228
    C = 12.5
    r0 = 720.
    s0 = 720.

    lmda = np.radians(lon)
    phi = np.radians(lat)

    r = 2 * R / C * np.sin(lmda) * np.sin( (np.pi/4.) - (phi/2.) ) + r0
    s = 2 * R / C * np.cos(lmda) * np.sin( (np.pi/4.) - (phi/2.) ) + s0

    return (r,s)


