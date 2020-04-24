from proj_class import SentinelPass
import numpy as np
from pprint import pprint as pp

first_test = SentinelPass('../data/S2A_MSIL2A_20200418T164901_N0214_R026_T16TCM_20200418T210937.SAFE/GRANULE/L2A_T16TCM_A025191_20200418T165421/IMG_DATA/R10m/T16TCM_20200418T164901_B04_10m.jp2',
                          '../data/S2A_MSIL2A_20200418T164901_N0214_R026_T16TCM_20200418T210937.SAFE/GRANULE/L2A_T16TCM_A025191_20200418T165421/IMG_DATA/R10m/T16TCM_20200418T164901_B08_10m.jp2',
                          '../data/S2A_MSIL2A_20200418T164901_N0214_R026_T16TCM_20200418T210937.SAFE/GRANULE/L2A_T16TCM_A025191_20200418T165421/IMG_DATA/R10m/T16TCM_20200418T164901_B02_10m.jp2',
                          './farm_simple.geojson')

if __name__ == '__main__':
    #pp(first_test.avail_paddocks())
    pp(first_test.paddock_stats('East 18 South', 'evi'))