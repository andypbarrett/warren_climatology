'''
Plots daily precipitation
'''
import os
import xarray as xr
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import cartopy.crs as ccrs
import cartopy.feature as cfeature
import datetime as dt

def product_metadata(reanalysis):

    metadata = {
                'CFSR': {'path': '/disks/arctic5_raid/abarrett',
                         'varname': 'PRATE',
                         'name': 'CFSR',
                         'ffmt': 'CFSR.flxf06.gdas.PRATE.{:4d}{:02d}{:02d}.nc',
                         'scale': 86400.}
               }

    return metadata[reanalysis]

def get_filepath(reanalysis, date):

    meta = product_metadata(reanalysis)

    return os.path.join(meta['path'],
                        reanalysis,
                        meta['varname'],
                        '{:4d}'.format(date.year),
                        '{:02d}'.format(date.month),
                        meta['ffmt'].format(date.year,date.month,date.day))

def set_colormap():
    '''Defines colormap with NSW Precip colors'''
    
    colors = [
        "#04e9e7",  # 0.01 - 0.10 inches
        "#019ff4",  # 0.10 - 0.25 inches
        "#0300f4",  # 0.25 - 0.50 inches
        "#02fd02",  # 0.50 - 0.75 inches
        "#01c501",  # 0.75 - 1.00 inches
        "#008e00",  # 1.00 - 1.50 inches
        "#fdf802",  # 1.50 - 2.00 inches
        "#e5bc00",  # 2.00 - 2.50 inches
        "#fd9500",  # 2.50 - 3.00 inches
        "#fd0000",  # 3.00 - 4.00 inches
        "#d40000",  # 4.00 - 5.00 inches
        "#bc0000",  # 5.00 - 6.00 inches
        "#f800fd",  # 6.00 - 8.00 inches
        "#9854c6",  # 8.00 - 10.00 inches
        "#fdfdfd"   # 10.00+
    ]
    cmap = mcolors.ListedColormap(colors)
    cmap.set_over('white')
    cmap.set_under('white')

    return cmap

def set_norm(cmap):
    '''Defines a Boundary Normalization'''
    
    levels=[0.2, 2.5, 5., 10., 20., 30., 40.,
            50., 60., 80., 100., 125., 150.,
            200., 250., 500.]
    return mcolors.BoundaryNorm(levels, cmap.N, clip=False)

def get_precip(reanalysis, date):
    '''
    Gets a precipitation grid for a given reanalysis product and data

    reanalysis - reanalysis product: ERA-Interim, CFSR, CFSR2, 
                                     MERRA, MERRA2, ERA5, ASR

    date - datetime date
    
    Returns
    -------
    dataarray containing daily total precip
    '''

    m = product_metadata(reanalysis)
    
    ds = xr.open_dataset(get_filepath(reanalysis, date))

    da = ds[m['varname']] * m['scale']
    proj = ccrs.PlateCarree()
    extent = [da.coords['lon_0'].values[0],
              da.coords['lon_0'].values[-1],
              da.coords['lat_0'].values[0],
              da.coords['lat_0'].values[-1]]
    origin = 'lower'
    
    return da, proj, extent, origin


def main():

    date = dt.datetime(1979,8,1)
    prec, prec_proj, prec_ext, prec_ori = get_precip('CFSR',date)

    print prec.coords['lon_0']
    print prec.coords['lat_0']
    
    return

    # Make plot
    cmap = set_colormap() # Define colormap
    norm = set_norm(cmap) # Define normalization

    #proj = ccrs.LambertAzimuthalEqualArea(central_longitude=0.0,
    #                                      central_latitude=90.)
    proj = ccrs.PlateCarree()
    
    fig = plt.figure(figsize=(15,10))
    ax = plt.axes(projection=proj) 
    #ax.set_extent([0.,359.99,50.,90.], ccrs.PlateCarree())
                   
    myplot = prec.plot(cmap=cmap, norm=norm,
                       transform=ccrs.PlateCarree(), ax=ax)
    #myplot = ax.imshow(prec, cmap=cmap, norm=norm,
    #                   transform=prec_proj, origin=prec_ori)
    #, extent=prec_ext,
    #                   origin=prec_ori)

    print prec_ext
    
    ax.add_feature(cfeature.COASTLINE)
    
    plt.show()
    
    return

if __name__ == "__main__":
    main()
