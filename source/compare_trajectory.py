# Plots the trajectories of north pole drifting stations
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cfeature

def compare_trajectory(lon0, lat0, lon1, lat1, title=None):

    plot_crs = ccrs.NorthPolarStereo()
    data_crs = ccrs.PlateCarree()

    # Transform lat, lon to projected coords to avoid issues
    # with trajectory crossing prime-meridian
    x0 = plot_crs.transform_points(data_crs, lon0, lat0)
    x1 = plot_crs.transform_points(data_crs, lon1, lat1)
    
    fig = plt.figure(figsize=(10,10))
    ax = plt.subplot(projection=plot_crs)

    ax.set_extent([-180,180,65,90], ccrs.PlateCarree())

    ax.add_feature(cfeature.OCEAN)
    ax.add_feature(cfeature.LAND)

    ax.plot(x0[:,0], x0[:,1], color='r')
    ax.plot(x1[:,0], x1[:,1], color='b')
    
    ax.set_title(title)

    return (fig, ax)

def main(station):

    import os, glob
    
    from readers.npsnow import read_uniformat
    from readers.npsnow import read_position

    # Climate atlas locations
    home = '/home/apbarret/data/'
    diri = 'US_Russian_Arctic_Atlas_Arctic_Climatology_Project_Arctic_Meteorology_Climate_Atlas/DATA/FLOATING_PLATFORMS/RUSSIAN_DRIFT'
    df0 = read_uniformat( os.path.join(home,diri,'uni.np-{:02d}.dat'.format(station)) )

    diri = '/home/apbarret/data/NPSNOW/position'
    df1 = read_position( os.path.join(home,diri,'position.{:02d}'.format(station)) )
                                       
    compare_trajectory(df0['lon'].values, df0['lat'].values,
                       df1['lon'].values, df1['lon'].values,
                       title='NP-{:02d}'.format(station))

    plt.show()


if __name__ == "__main__":
    import sys
    
    main(int(sys.argv[1]))


    
