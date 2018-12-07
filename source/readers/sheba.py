# Reader functions for SHEBA data

import pandas as pd
import datetime as dt

def read_nipher(fp):
    """Reads nipher_data file"""
    if not fp:
        fp = '/home/apbarret/data/SHEBA/Precipitation/nipher_data'

    
