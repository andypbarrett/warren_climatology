#----------------------------------------------------------------------
# Code to merge meteorological data files and precipitation files for
# North Pole drifting stations
#----------------------------------------------------------------------
import os
import glob
import re

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

import readers.npsnow as npsnow

NPSNOW_PATH = '/home/apbarret/data/NPSNOW'

def get_station_list():
    """Returns list of station ids, extracted from met filenames"""
    filelist = glob.glob(os.path.join(NPSNOW_PATH,'met','metnp_??.dat'))
    id = [re.search('(?<=metnp_)\d{2}',f).group(0) for f in sorted(filelist)]
    return id

def met_filename(sid):
    """Returns met file name for station id"""
    return os.path.join(NPSNOW_PATH,'met','metnp_{:2s}.dat'.format(sid))

def precip_filelist(sid):
    """Returns list of precip files for station id"""
    filelist = glob.glob(os.path.join(NPSNOW_PATH, 'precip', 'np_{:2s}_??.pre'.format(sid)))
    return sorted(filelist)

def get_precip(sid):
    """Reads a list of precip files and concatenates them"""
    return pd.concat([npsnow.read_precip(f) for f in precip_filelist(sid)])
    
def merge_one_station(sid):
    """Reads met and precip files, merges files, writes to csv"""

    met = npsnow.read_met(met_filename(sid))
    metDay = met.resample('D').mean()
    preDay = get_precip(sid)
    
    merged_df = pd.concat([metDay,preDay], axis=1, sort=False)
    merged_df = merged_df.rename({'amount':'PRECIP', 'type':'PTYPE'}, axis=1)
    return merged_df

def myFmtr(v, pos=None):
    d = mdates.num2date(v)
    if d.month == 1:
        return d.strftime('%b\n%Y')
    else:
        return d.strftime('%b')

def plot_station_met(df, title='', pngfile=None):
    """Plots TAIR, RH, WSPD and Precip amount and type"""
    fig, ax = plt.subplots(4,1, figsize=(11,10), sharex=False)

    xlim = (df.index[0],df.index[-1])

    # TAIR
    df['TAIR'].plot(ax=ax[0])
    ax[0].set_xlim(*xlim)
    ax[0].set_ylim(df['TAIR'].min(), 10.)
    ax[0].set_ylabel('$^oC$')
    ax[0].axhline(0.,color='k')
    plt.setp(ax[0].get_xticklabels(), visible=False)
    ax[0].text(0.9, 0.9, 'Air Temperature', horizontalalignment='center',
               transform=ax[0].transAxes, fontsize=12)
    
    # RH
    df['RH'].plot(ax=ax[1]) #, sharex=ax[0])
    ax[1].set_xlim(*xlim)
    ax[1].set_ylabel('%')
    plt.setp(ax[1].get_xticklabels(), visible=False)
    ax[1].text(0.9, 0.9, 'Relative Humidity', horizontalalignment='center',
               transform=ax[1].transAxes, fontsize=12)

    # WSPD
    df['WSPD'].plot(ax=ax[2]) #, sharex=ax[0])
    ax[2].set_xlim(*xlim)
    ax[2].axhline(6.,color='k')
    ax[2].set_ylabel('m/s')
    plt.setp(ax[2].get_xticklabels(), visible=False)
    ax[2].text(0.9, 0.9, 'Wind Speed', horizontalalignment='center',
               transform=ax[2].transAxes, fontsize=12)

    bar_color = ['b' if ptype == 1 else '0.3' for ptype in df['PTYPE']]
    ax[3].bar(df.index, df['PRECIP'], width=1, color=bar_color) #, sharex=ax[0])
    ax[3].set_xlim(*xlim)
    ax[3].set_ylabel('mm')
    ax[3].text(0.9, 0.9, 'Precipitation', horizontalalignment='center',
               transform=ax[3].transAxes, fontsize=12)

    # Formatting for axis 3
    #myFmt = mdates.DateFormatter('%b')
    #print ( )
    ax[3].xaxis.set_major_formatter(plt.FuncFormatter(myFmtr))
    
    fig.suptitle(title, fontsize=20)

    if pngfile:
        fig.savefig(pngfile)

    plt.close(fig)
    
def main(doplot=False, nowrite=False):

    station_id = get_station_list()

    # Get snowstake data for snow depth
    snwstk_path = '/home/apbarret/data/NPSNOW/snow/measured/snwstake.dat'
    snwstk = npsnow.read_snowstake(snwstk_path)

    for sid in station_id:
        # Skip first 2 stations
        if int(sid) > 2:
            df = merge_one_station(sid)

            df['SDEPTH'] = snwstk[snwstk.station == int(sid)].snowdepth

            if doplot:
                pngfile = os.path.join(NPSNOW_PATH,'my_combined_met',
                                       'npmet_{:s}.png'.format(sid))
                print ('Plotting {:s}'.format(pngfile))
                plot_station_met(df, title='Station {:s}'.format(sid),
                                 pngfile=pngfile)
            if not nowrite:
                csvfile = os.path.join(NPSNOW_PATH,'my_combined_met',
                                       'npmet_{:s}_combined.csv'.format(sid))
                print ('Writing combined data to {:s}'.format(csvfile))
                df.to_csv(csvfile)
    
if __name__ == "__main__":
    main(doplot=False, nowrite=False)
    
