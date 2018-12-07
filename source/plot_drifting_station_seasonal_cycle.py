import matplotlib     # If running over ssh  
matplotlib.use('agg')

import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import numpy as np
import pandas as pd
import datetime as dt

def get_bogdanova_monthly():
    """Returns monthly corrected precipitation from Bogdanova et al.  2002."""
    return pd.DataFrame([12.5, 9.5, 9.5, 7.4, 9.2, 12.4, 23.7, 22.4, 20.3, 15.3, 11.1, 11.1,],
                        index=np.arange(1,13), columns=['P'])

def read_data():
    """
    Reads csv file containing precipitation along trajectories
    """
    which_season = {1: 'DJF', 2: 'DJF', 3: 'MAM', 4: 'MAM',
                    5: 'MAM', 6: 'JJA', 7: 'JJA', 8: 'JJA',
                    9: 'SON', 10: 'SON', 11: 'SON', 12: 'DJF'}
    
    filepath = 'np_reanalysis_month_comparison.csv'
    df = pd.read_csv(filepath, index_col=0)
    df['Date'] = [dt.datetime.strptime(t,'%Y-%m-%d') for t in df['Date']] # Convert date string to datetime
    df['Season'] = [which_season[m] for m in df['Date'].dt.month] # Determine season
    return df

def main():
    """
    Makes plot of monthly precipitation from reanalysis and corrected observations 
    from Yang and Bogdanova.
    """

    P_Bog = get_bogdanova_monthly()

    P_df = read_data()
    P_mon = P_df.groupby(P_df['Date'].dt.month).mean()
    P_mon = P_mon.drop(['Lat','Lon','NP'], axis=1)
    P_mon = P_mon.rename(columns={'Pc':'Pyang'})
    P_mon['Pbog'] = P_Bog['P']
                         
    # Plot data

    x = np.arange(1,13)
    xb = x-0.25
    xy = x+0.25
    width = 0.3

    fig, ax = plt.subplots(figsize=(10,7))

    ax.set_xlim(0.5,12.5)
    
    ax.bar(xy, P_mon['Pyang'], width=width, color='0.3', edgecolor='none',
            align='center', label='Yang')
    ax.bar(xb, P_mon['Pbog'], width=width, color='0.6', edgecolor='none',
            align='center', label="Bogdanova")

    reanalyses = ['ERAI','MERRA2','MERRA','CFSR','JRA55']
    symbols = ['o','v','s','X','*']
    for s, r in zip(symbols,reanalyses):
        ax.plot(x, P_mon[r+'_prectot'], marker=s, linestyle='',
                markersize=10, label=r)
#        ax.plot(x, P_mon[r+'_prectot'], marker=s, linestyle='-',
#                markersize=15, linewidth=1.5, label=r)
#        ax.plot(x, P_mon[r+'_prectot'], linestyle='-', linewidth=3, label=r)
        
    ax.set_ylabel('mm', fontsize=20)

    # Make ticks at 'month' boundaries and ticklabels at center
    major = np.arange(1.,13.,1.)
    minor = np.arange(0.5,13.,1.)
    ax.xaxis.set_major_locator(ticker.FixedLocator(major))
    ax.xaxis.set_minor_locator(ticker.FixedLocator(minor))
    ax.set_xticklabels(['J','F','M','A','M','J','J','A','S','O','N','D'],
                       fontsize=20)
    ax.tick_params('x', which='major', length=0, labelsize=20)
    ax.tick_params('x', which='minor', width=1., length=10)
    ax.tick_params('y', labelsize=20)

    ax.legend(fontsize=17, frameon=False, loc=(0.02,0.5))

    fig.savefig('drifting_station_seasonal_cycle_with_reanalysis.png')
                
if __name__ == "__main__":
    main()
    
        
    
