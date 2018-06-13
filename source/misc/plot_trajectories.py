# Plots the trajectories of north pole drifting stations
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cfeature
import os, glob

from readers.npsnow import read_uniformat

def main(title=None):

    plot_crs = ccrs.NorthPolarStereo()
    data_crs = ccrs.PlateCarree()

    # Get list of files
    diri = '/home/apbarret/data/US_Russian_Arctic_Atlas_Arctic_Climatology_Project_Arctic_Meteorology_Climate_Atlas/DATA/FLOATING_PLATFORMS/RUSSIAN_DRIFT'
    fileList = glob.glob( os.path.join(diri,'uni.np-??.dat') )

    # Set up plot
    fig = plt.figure(figsize=(10,10))
    ax = plt.subplot(projection=plot_crs)

    ax.set_extent([-180,180,65,90], ccrs.PlateCarree())

    ax.add_feature(cfeature.OCEAN)
    ax.add_feature(cfeature.LAND)

    if title: ax.set_title(title)

    for f in fileList:
        df = read_uniformat(f)

        if any(df.index.year > 1979):
            
        # Transform lat, lon to projected coords to avoid issues
        # with trajectory crossing prime-meridian
            x = plot_crs.transform_points(data_crs, df['lon'].values, df['lat'].values)
            ax.plot(x[:,0], x[:,1])
    
    plt.show()
    fig.savefig('np_drifting_station_trajectories_1979to1991.png')

if __name__ == "__main__":
    main(title='Russian North Pole Drifting Stations 1979-1991')


    
