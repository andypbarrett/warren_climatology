# Plots the trajectories of north pole drifting stations
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cfeature

def plot_trajectory(lon, lat, title=None):

    plot_crs = ccrs.NorthPolarStereo()
    data_crs = ccrs.PlateCarree()

    # Transform lat, lon to projected coords to avoid issues
    # with trajectory crossing prime-meridian
    x = plot_crs.transform_points(data_crs, lon, lat)
    
    fig = plt.figure(figsize=(10,10))
    ax = plt.subplot(projection=plot_crs)

    ax.set_extent([-180,180,65,90], ccrs.PlateCarree())

    ax.add_feature(cfeature.OCEAN)
    ax.add_feature(cfeature.LAND)

    ax.plot(x[:,0], x[:,1])
    
    ax.set_title(title)

    return (fig, ax)

def main(station):

    import os, glob
    
    from readers.npsnow import read_uniformat

    diri = '/home/apbarret/data/US_Russian_Arctic_Atlas_Arctic_Climatology_Project_Arctic_Meteorology_Climate_Atlas/DATA/FLOATING_PLATFORMS/RUSSIAN_DRIFT'
    df = read_uniformat( os.path.join(diri,'uni.np-{:02d}.dat'.format(station)) )
    
    plot_trajectory(df['lon'], df['lat'], title='NP-{:02d}'.format(station))

    plt.show()


if __name__ == "__main__":
    import sys
    
    main(int(sys.argv[1]))


    
