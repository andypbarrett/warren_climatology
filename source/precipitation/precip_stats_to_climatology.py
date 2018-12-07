import xarray as xr

def precip_stats_to_climatology(fili, start_year=1981, end_year=2015):
    """
    Calculates average climatology for annual data - either Jan to Dec or accummulation period
    """

    ds = xr.open_dataset(fili)

    year = ds['time'].dt.year 
    dsClm = ds.isel( time=( (year >= start_year) & (year <= end_year) ) ).mean(dim='time')

    print (dsClm)

    filo = fili.replace('annual','annual.clm')
    print (filo)
    return

    dsClm.to_netcdf(filo)

    return

if __name__ == "__main__":

    import argparse

    parser = argparse.ArgumentParser( description='Calculates climatology from annual data' )
    parser.add_argument('fili', type=str, help='path to annual file')
    parser.add_argument('--start_year', '-sy', default=1981,
                        help='First year for climatology')
    parser.add_argument('--end_year', '-ey', default=2015,
                        help='Last year for climatology')
    args = parser.parse_args()

    precip_stats_to_climatology(args.fili, start_year=args.start_year, end_year=args.end_year)
    

    
    
    
