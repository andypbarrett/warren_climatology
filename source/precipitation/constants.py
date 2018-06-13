# Constants and parameters used in precipitation analysis

filepath = {
            'ERA-Interim': {'path': '/disks/arctic5_raid/abarrett/ERA_Interim/daily/{:s}/{}',
                            'ffmt': 'era_interim.{}.{}.day.nc'},
            'MERRA2': {'path': '/disks/arctic5_raid/abarrett/MERRA2/daily/{}/{:4d}/{:02d}',
                       'ffmt': 'MERRA2_?00.tavg1_2d_flx_Nx.{}.{}??.nc4'},
            'CFSR': {'path': '/disks/arctic5_raid/abarrett/CFSR/{}/{:4d}/{:02d}',
                     'ffmt': 'CFSR.flxf06.gdas.{:s}.{}??.nc'},
            'CFSR2': {'path': '/disks/arctic5_raid/abarrett/CFSR2/{}/{:4d}/{:02d}',
                      'ffmt': 'CFSR2.flxf06.gdas.{:s}.{}??.nc'},
            'MERRA': {'path': '/disks/arctic5_raid/abarrett/MERRA/daily/{}/{:4d}/{:02d}',
                      'ffmt': 'MERRA???.prod.{:s}.assim.tavg1_2d_flx_Nx.{:s}??.nc4'},
            'JRA55': {'path': '/disks/arctic5_raid/abarrett/JRA55/{}/{:4d}/{:02d}',
                      'ffmt': 'fcst_phy2m.061_tprat.reg_tl319.{}.{:s}??.nc4'}
            }

vnamedict = {
             'ERA-Interim': {'PRECIP': {'name': 'PRECTOT', 'scale': 1.e3},
                             'T2M': {'name': 'T2M', 'scale': 1}},
             'CFSR': {'PRECIP': {'name': 'PRATE', 'scale': 86400.},
                      'T2M': {'name': 'T2M', 'scale': 1.}},
             'CFSR2': {'PRECIP': {'name': 'PRATE', 'scale': 86400.},
                       'T2M': {'name': 'T2M', 'scale': 1.}},
             'MERRA': {'PRECIP': {'name': 'PRECTOT', 'scale': 1.}},
             'MERRA2': {'PRECIP': {'name': 'PRECTOT', 'scale': 1.}},
             'JRA55': {'PRECIP': {'name': 'PRECTOT', 'scale': 1./8.}}
            }
#             'MERRA2': {},
#             'CFSR2': {},
#             'MERRA': {}}
