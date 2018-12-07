# Crawls the NASA Earthdata OpenDAP server to explore datasets
#
# Arguments
# ---------
# reanalysis:   Name of reanalysis.  Currently MERRA or MERRA2
# data_product: Shortname for data product: e.g. MAT1NXFLX
# start_date:   Date to start search.  Default is 19790101
# end_date:     Date to end search.  Default present date
# 
# Returns: a list of files for a given data set
#
# 2018-01-04 A.P.Barrett <apbarret@nsidc.org>

import requests
import datetime as dt
import xml.etree.ElementTree as ET
from urllib.parse import urljoin
import os
import re

# overriding requests.Session.rebuild_auth to mantain headers when redirected
class SessionWithHeaderRedirection(requests.Session):
 
    AUTH_HOST = 'urs.earthdata.nasa.gov'
 
    def __init__(self, username, password):
        super(SessionWithHeaderRedirection, self).__init__()
        self.auth = (username, password)
        
    # Overrides from the library to keep headers when redirected to or from
    # the NASA auth host.
    def rebuild_auth(self, prepared_request, response):
        
        headers = prepared_request.headers
        url = prepared_request.url
        
        if 'Authorization' in headers:
            
            original_parsed = requests.utils.urlparse(response.request.url)
            redirect_parsed = requests.utils.urlparse(url)
            
            if (original_parsed.hostname != redirect_parsed.hostname) and \
               (redirect_parsed.hostname != self.AUTH_HOST) and \
               (original_parsed.hostname != self.AUTH_HOST):
                del headers['Authorization']
                
        return
 
def get_product_url(reanalysis, time, variable, year=None):

    from tables import CatalogUrl
    
    if year:
        result = '{:s}/{:4d}/catalog.xml'.format(CatalogUrl[reanalysis][time][variable],year)
    else:
        result = '{:s}/catalog.xml'.format(CatalogUrl[reanalysis][time][variable])
    
    return result

def crawl(catalog, session):

    ns = {'thredds': 'http://www.unidata.ucar.edu/namespaces/thredds/InvCatalog/v1.0',
          'xlink': 'http://www.w3.org/1999/xlink'}

    try:
        # Get xml
        response = session.get(catalog, stream=True)
        response.raise_for_status()

        xml = ET.fromstring(response.content)

        for subdir in xml.iterfind('.//{%s}catalogRef' % ns['thredds']):
            link = subdir.get('{%s}href' % ns['xlink'])
            for dataset in crawl(urljoin(catalog, link), session):
                yield dataset

        for dataset in xml.iterfind('.//{%s}access' % ns['thredds']):
            if dataset.attrib['serviceName'] == 'dap': yield dataset.attrib['urlPath']

    except requests.exceptions.HTTPError as e:
        # handle any errors here
        print(e)


def nasa_crawler(catalog, filo=None, to_stdout=False):
        #reanalysis, variable, time_resolution='hourly', year=None, month=None, filo=None, to_stdout=False):
    """
    Explores NASA catalogs for a given data product and returns a list of files.

    ****** Currently takes xml catalog url as argument *****

    The search can be limited to year and month.

    Arguments
    ---------
    reanalysis - Name of NASA reanalysis (e.g. MERRA or MERRA2)
    product -    Shortname for data product: e.g. MAT1NXFLX
    time_resolution - daily or monthly (default daily)
    year -       Year to search (default is None - search all years)
    month -      Month to search (default is None - search all months for a given year).
                 Is ignored is year is not set.
    filo -       File to write list to - if no filo set then filename is
                 <reanalysis>_<product>_filelist.txt

    Returns
    -------
    None - file list is written to file
    """
    
    # create session with the user credentials that will be used to authenticate access to the data    
    username = 'apbarret'
    password= 'T0talBollocks'
    session = SessionWithHeaderRedirection(username, password)

    # Get the url of the file we wish to retrieve
    #catalog = get_product_url(reanalysis, time_resolution, variable, year=year)

    # Get all datasets underneath the catalog url
    dataset_list = crawl(catalog, session)

    # Add servername to dataset
    server = re.search('(https.+)(?=/MERRA)',catalog).groups()[0]
    fileList = [server+dataset for dataset in dataset_list]

    # Write to file
    if to_stdout:
        for dataset in fileList:
            print (dataset)
    else:
        if not filo: filo = os.path.join('.','{:s}_{:s}_filelist.txt'.format(reanalysis,variable))
        f = open(filo, 'w')
        for dataset in fileList:
            f.write(dataset+'\n')
        f.close()

    session.close()
    
if __name__ == "__main__":

    import argparse

    parser = argparse.ArgumentParser(description='Retrieves filelist for NASA reanalysis')
    parser.add_argument('catalog', type=str,
                        help='URL for XML catalog page')
#    parser.add_argument('reanalysis', metavar='reanalysis', type=str,
#                        help='Name of NASA reanalysis: MERRA, MERRA2')
#    parser.add_argument('variable', metavar='variable', type=str,
#                        help='Name of variable to download: e.g. SLP')
    parser.add_argument('--fileout', '-o', type=str, action='store', default=None,
                        help='name of output file')
#    parser.add_argument('--year', '-y', type=int, action='store', default=None,
#                        help='year (YYYY) - stale')
#    parser.add_argument('--month', '-m', type=int, action='store', default=1,
#                        help='month (MM) - stale')
#    parser.add_argument('--time_resolution', '-tr', type=str, action='store', default='hourly',
#                        help='Time resolution for data (hourly, daily, monthly)')
    parser.add_argument('--to_stdout', '-so', action='store_true')
    
    args = parser.parse_args()

#    nasa_crawler(args.reanalysis, args.variable, year=args.year, month=args.month,
#                 time_resolution=args.time_resolution, filo=args.fileout, to_stdout=args.to_stdout)

    nasa_crawler(args.catalog, filo=args.fileout, to_stdout=args.to_stdout)
