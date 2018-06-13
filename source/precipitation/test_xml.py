# Test using the xml library

import xml.etree.ElementTree as ET
from urlparse import urljoin

def crawler(catalog):

    ns = {'thredds': 'http://www.unidata.ucar.edu/namespaces/thredds/InvCatalog/v1.0',
          'xlink': 'http://www.w3.org/1999/xlink'}

    
    tree = ET.parse(catalog)

    # Need some code to deal with extra 2 lines at head of catalog

    for subdir in tree.iterfind('.//{%s}catalogRef' % ns['thredds']):
        link = subdir.get('{%s}href' % ns['xlink'])
        print urljoin(catalog, link)

    for dataset in tree.iterfind('.//{%s}dataset[@urlPath]' % ns['thredds']):
        print dataset
        
catalog = './test.xml'
crawler(catalog)


