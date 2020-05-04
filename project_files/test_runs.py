from proj_class import SentinelPass
import numpy as np
from pprint import pprint as pp
import os

if __name__ == '__main__':
    first_test = SentinelPass('S2B_MSIL2A_20200420T163829_N0214_R126_T16TCM_20200420T210016.SAFE',
                              './farm_simple.geojson')
    first_test.geotiff_to_png('ndvi')
    first_test.geotiff_to_png('evi')
    first_test.paddock_stats('Farm boundary', 'ndvi')
    first_test.paddock_stats('Farm boundary', 'evi')