import pandas as pd
import matplotlib.pyplot as plt

snow_color='0.8'
rain_color='cornflowerblue'

def get_month_data():

    filepath = '/home/apbarret/src/SnowOnSeaIce/source/precipitation/'\
               'merra2_regional_snowfall_fraction.v2.csv'
    df = pd.read_csv(filepath, header=0, skiprows=[1,2], index_col=0, parse_dates=True)
    return df

def get_annual_data():

    filepath = '/home/apbarret/src/SnowOnSeaIce/source/precipitation/'\
               'merra2_regional_snowfall_fraction.annual.v2.csv'
    df = pd.read_csv(filepath, header=0, skiprows=[1,2], index_col=0, parse_dates=True)
    return df

def plot_month_data(df, regions=None, fileout=None):
    """Plots monthly snowfall fraction"""

    if not regions:
        regions = df.columns
        
    fig, ax = plt.subplots(len(regions), 1, figsize=(11,8))

    for ip, (axis, region) in enumerate(zip(ax, regions)):
        axis.set_facecolor(rain_color)
        axis.fill_between(df[region].index, 0., df[region], color=snow_color)
        axis.set_ylim(0,1.)
        axis.set_xlim(df.index[0],df.index[-1])
        if ip != len(regions)-1:
            axis.set_xticks([])
            axis.set_xticklabels([])
        axis.text(0.01, 0.05, region, verticalalignment='bottom', transform=axis.transAxes,
                  bbox=dict(facecolor='white', edgecolor='white', alpha=0.))

    fig.suptitle('Fraction of Precipitation Falling as Snow in MERRA2', fontsize=16, y=0.92)

    if fileout:
        fig.savefig(fileout)
    else:
        plt.show()

    return

def plot_annual_data(df, regions=None, fileout=None):
    """Plots annual snowfall fraction"""

    if not regions:
        region = df.columns
        
    fig, ax = plt.subplots(len(regions), 1, figsize=(11,8))

    for ip, (axis, region) in enumerate( zip(ax, regions) ):
        axis.fill_between(df.index, 0, df[region], step='pre', color=snow_color)
        axis.set_facecolor(rain_color)
        axis.set_ylim(0,1)
        axis.set_xlim(df.index[0], df.index[-2])
        if ip != len(regions)-1:
            axis.set_xticks([])
            axis.set_xticklabels([])
        else:
            axis.text(0.99, 0.05, 'Snow',
                      verticalalignment='bottom', horizontalalignment='right',
                      transform=axis.transAxes)
            axis.text(0.99, 0.95, 'Rain',
                      verticalalignment='top', horizontalalignment='right',
                      transform=axis.transAxes)
        axis.text(0.01, 0.05, region, verticalalignment='bottom', transform=axis.transAxes)

    fig.suptitle('Fraction of Annual Precipitation Falling as Snow in MERRA2', fontsize=16, y=0.92)

    if fileout:
        fig.savefig(fileout)
    else:
        plt.show()

    return
    
def main():

    these_regions = ['CENTRAL_ARCTIC', 'BEAUFORT', 'CHUKCHI', 'BARENTS',
                     'KARA', 'LAPTEV', 'EAST_SIBERIAN', 'GREENLAND']
    
    month_data = get_month_data()
    annual_data = get_annual_data()
    
    plot_month_data(month_data, regions=these_regions,
                    fileout='merra2_arctic_region_snow_fraction.month.png')

    # Excludes 2018 as this is not a full year
    plot_annual_data(annual_data.iloc[:-2,:], regions=these_regions,
                     fileout='merra2_arctic_region_snow_fraction.annual.png')
    
    return

if __name__ == "__main__":
    main()
    
