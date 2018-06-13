#!/usr/bin/env python

import netCDF4
from cookielib import CookieJar
from urllib import urlencode
 
import urllib2
 
 
# The user credentials that will be used to authenticate access to the data
 
username = "apbarret"
password = "FurRyM0nchkin"
  
 
# Create a password manager to deal with the 401 reponse that is returned from
# Earthdata Login
 
password_manager = urllib2.HTTPPasswordMgrWithDefaultRealm()
password_manager.add_password(None, "https://urs.earthdata.nasa.gov", username, password)
 
# Create a cookie jar for storing cookies. This is used to store and return
# the session cookie given to use by the data server (otherwise it will just
# keep sending us back to Earthdata Login to authenticate).  Ideally, we
# should use a file based cookie jar to preserve cookies between runs. This
# will make it much more efficient.
 
cookie_jar = CookieJar()

#---------------------------------------------------------------------------
thisVar = 'PRECTOT'

url = "https://goldsmr4.gesdisc.eosdis.nasa.gov:443/opendap/MERRA2_MONTHLY/M2TMNXFLX.5.12.4/1980/MERRA2_100.tavgM_2d_flx_Nx.198001.nc4"

f = netCDF4.Dataset(url,"r")

var = f.variables[thisVar]
print var[:,:,:]
#data = var[:]
#data.shape

f.close()
