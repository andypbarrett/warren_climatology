import matplotlib.pyplot as plt

from get_arctic_regional_stats import read_arctic_regional_stats

filepath = {
    'ERAI': 'erai_regional_stats.csv',
    'CFSR': 'cfsr_regional_stats.csv',
    'MERRA': 'merra_regional_stats.csv',
    'MERRA2': 'merra2_regional_stats.csv',
    'JRA55': 'jra55_regional_stats.csv',
           }

def _get_prectot_climatology(df):
    """
    Calculates prectot climatology for each region

    Returns: dataFrame
    """
    return df.xs('prectot',level=1,axis=1).groupby(df.index.month).mean()

# Get the data
data = {}
for reanalysis, path in filepath.items():
    data[reanalysis] = read_arctic_regional_stats(path)

# Compute climatologies of prectot
climo = {}
for reanalysis, df in data.items():
    climo[reanalysis] = _get_prectot_climatology(df)

# Plot climatologies from reanalyses for each Arctic Ocean region 
region_list = ['CENTRAL_ARCTIC','BEAUFORT','CHUKCHI','BARENTS','KARA','LAPTEV','EAST_SIBERIAN']

fig, axes = plt.subplots(3,3, figsize=(15,15))

for region, ax in zip(region_list, axes.flatten()):

    ax.set_ylabel('Total Precipitation (mm)')
    ax.set_xlabel('Month')
    ax.set_title(region)

    ax.plot(climo['ERAI'][region], label='ERAI')
    ax.plot(climo['CFSR'][region], label='CFSR')
    ax.plot(climo['MERRA'][region], label='MERRA')
    ax.plot(climo['MERRA2'][region], label='MERRA2')
    ax.plot(climo['JRA55'][region], label='JRA55')

    if region == 'CENTRAL_ARCTIC': ax.legend()

plt.tight_layout()
plt.show()

    
