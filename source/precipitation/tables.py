#----------------------------------------------------------------------
# Contains dictionaries and constants for downloading reanalysis datasets
#----------------------------------------------------------------------

m2version = '5.12.4'

CatalogUrl = {'MERRA2': {
                         'monthly': {
                                     'SLP':  'https://goldsmr4.gesdisc.eosdis.nasa.gov:443/opendap/MERRA2_MONTHLY/M2TMNXSLV.{:s}'.format(m2version),
                                     'PS':   'https://goldsmr4.gesdisc.eosdis.nasa.gov:443/opendap/MERRA2_MONTHLY/M2TMNXSLV.{:s}'.format(m2version),
                                     'T2M':  'https://goldsmr4.gesdisc.eosdis.nasa.gov:443/opendap/MERRA2_MONTHLY/M2TMNXSLV.{:s}'.format(m2version),
                                     'H500': 'https://goldsmr4.gesdisc.eosdis.nasa.gov:443/opendap/MERRA2_MONTHLY/M2TMNXSLV.{:s}'.format(m2version),
                                     'TQV':  'https://goldsmr4.gesdisc.eosdis.nasa.gov:443/opendap/MERRA2_MONTHLY/M2TMNXSLV.{:s}'.format(m2version),
                                     'PRECTOT': 'https://goldsmr4.gesdisc.eosdis.nasa.gov:443/opendap/MERRA2_MONTHLY/M2TMNXSLV.{:s}'.format(m2version),
                                    },
                         'production': {
                                       },
                        },
              'MERRA': {
                       },
              }
                
            
