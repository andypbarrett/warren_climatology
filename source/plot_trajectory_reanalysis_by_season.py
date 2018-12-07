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

def scatter_plot(df, x, y, ax=None, xlabel='X', ylabel='Y', title='',
                 xmax=None, xlabel_visible=True, ylabel_visible=True):
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
    if not xmax:
        xmax = max(df[[x,y]].max().values)
        xmax = np.ceil(xmax/10.)*10.
    
    ax.set_xlim(0,xmax)
    ax.set_ylim(0,xmax)
    ax.set_aspect('equal','box')
    
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    #ax.set_title(title)
    plt.setp(ax.get_xticklabels(), visible=xlabel_visible)
    plt.setp(ax.get_yticklabels(), visible=ylabel_visible)

    ax.plot(xv, yv, 'ko', markersize=2.)
    ax.plot([0,xmax],[0,xmax], color='0.4')

    ax.text( 0.05, 0.90, 'Corr: {:5.2f}'.format(correlate(df,x,y)), transform=ax.transAxes )
    ax.text( 0.05, 0.82, 'RMSE: {:4.1f}'.format(rmse(df,x,y)), transform=ax.transAxes )
    ax.text( 0.05, 0.74, 'Bias: {:4.1f}'.format(bias(df,x,y)), transform=ax.transAxes )

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

def main():
    
    # Read data
    traj = read_data()

    # Plotting
    fig, ax = plt.subplots(4, 5, figsize=(15,9))
    ax = ax.flatten()

    plt.subplots_adjust(left=0.27, bottom=0.1, right=0.9, top=0.9, wspace=0.1, hspace=0.1)

    reanalysis = ['ERAI','CFSR','MERRA','MERRA2','JRA55']
    season = ['DJF','MAM','JJA','SON']
    #for ir, reanalysis in enumerate(['ERAI','CFSR','MERRA','MERRA2','JRA55']):
    for ir, (ssn, rnls) in enumerate([(ssn, rnls) for ssn in season for rnls in reanalysis]):
        
        if np.mod(ir,5) == 0:
            ylabel = 'Model (mm)'
            ylabel_visible=True
        else:
            ylabel = ' '
            ylabel_visible=False
            
        if np.floor_divide(ir,5) == 3:
            xlabel = 'Observed (mm)'
            xlabel_visible=True
        else:
            xlabel = ' '
            xlabel_visible=False
                
        scatter_plot(traj[traj['Season'] == ssn], 'Pc', rnls+'_prectot',
                     ax=ax[ir],
                     xlabel=xlabel,
                     ylabel=ylabel,
                     title=rnls+' '+ssn,
                     xmax=110.,
                     xlabel_visible=xlabel_visible,
                     ylabel_visible=ylabel_visible)

        #pos0 = ax[0].get_position()
    ty = 0.91
    tx0 = 0.33
    txd = 0.13
    plt.figtext(tx0, ty, 'ERA-Interim', fontsize=15, horizontalalignment='center', figure=fig)
    plt.figtext(tx0+(1*txd), ty, 'CFSR', fontsize=15, horizontalalignment='center', figure=fig)
    plt.figtext(tx0+(2*txd), ty, 'MERRA', fontsize=15, horizontalalignment='center', figure=fig)
    plt.figtext(tx0+(3*txd), ty, 'MERRA2', fontsize=15, horizontalalignment='center', figure=fig)
    plt.figtext(tx0+(4*txd), ty, 'JRA55', fontsize=15, horizontalalignment='center', figure=fig)
    
    ty0 = 0.82
    tyd = 0.21
    for iy, ssn in enumerate(season):
        plt.figtext(0.2, ty0-(iy*tyd), ssn, fontsize=15, verticalalignment='center', figure=fig,
                    rotation=90.)
        
    #plt.tight_layout()
    plt.show()

    fig.savefig('np_trajectory_reanalysis_scatter_by_season.png')

if __name__ == "__main__":
    main()
