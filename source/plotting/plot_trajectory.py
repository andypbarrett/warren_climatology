# Plots the trajectories of north pole drifting stations

def main():

    import matplotlib.pyplot as plt
    import cartopy.crs as ccrs
    import cartopy.feature as cfeature
    import os, glob
    
    from readers.npsnow import read_position

    diri = '$HOME/data/NPSNOW/position'
    fileList = glob.glob(os.path.join(diri,'position.??'))
    
    fig = plt.figure(figsize=(10,10))
    ax = plt.subplot(projection=ccrs.NorthPolarStereo())

    ax.set_extent([-180,180,65,90], ccrs.PlateCarree())

    ax.add_feature(cfeature.OCEAN)
    ax.add_feature(cfeature.LAND)

    for f in fileList:
        df = read_position(f)
        ax.plot(df['lon'], df['lat'], transform=ccrs.PlateCarree())

    plt.show()


if __name__ == "__main__":
    main()


    
