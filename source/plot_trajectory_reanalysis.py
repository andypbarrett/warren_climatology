import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import datetime as dt

def rmse(df,x,y):                                                    
    return ( (df[x] - df[y])**2 ).mean()**0.5

def bias(df,x,y):                                                    
    return df[y].mean()/df[x].mean()

def correlate(df, x, y):                                             
    return df.loc[:,[x,y]].corr().iloc[0,1]  

def scatter_plot(df, x, y, ax=None, xlabel='X', ylabel='Y', title=''):
    """
    Makes scatter plot of two columns in a dataframe with names x and y.

    Arguments
    ---------
    df - dataframe
    x - name of x column
    y - name of y column
    ax - axes object
    xlabel - label for x-axis
    ylabel - label for y-axis
    title - plot title
    """

    xv = df[x]
    yv = df[y]

    
    # Get upper limit for plot
    xmax = max(df[[x,y]].max().values)
    xmax = np.ceil(xmax/10.)*10.

    ax.plot(xv, yv, 'bo')
    ax.plot([0,xmax],[0,xmax], color='0.4')

    ax.set_xlim(0,xmax)
    ax.set_ylim(0,xmax)
    ax.set_aspect('equal','box')
    
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    ax.set_title(title)

    ax.text( 0.05, 0.90, 'Corr: {:5.2f}'.format(correlate(df,x,y)), transform=ax.transAxes )
    ax.text( 0.05, 0.84, 'RMSE: {:4.1f}'.format(rmse(df,x,y)), transform=ax.transAxes )
    ax.text( 0.05, 0.78, 'Bias: {:4.1f}'.format(bias(df,x,y)), transform=ax.transAxes )
    return

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

    # Plotting
fig, ax = plt.subplots(3, 2, figsize=(9,9))
ax = ax.flatten()
    
for ir, reanalysis in enumerate(['ERAI','CFSR','MERRA','MERRA2','JRA55']):
    scatter_plot(traj, 'Pc', reanalysis+'_prectot', ax=ax[ir],
                 xlabel='Observed (mm)',
                 ylabel='Model (mm)',
                 title=reanalysis)

fig.delaxes(ax[5])
plt.tight_layout()
plt.show()

#fig.savefig('np_trajectory_reanalysis_scatter.png')
