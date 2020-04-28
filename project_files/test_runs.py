from proj_class import SentinelPass
import numpy as np
from pprint import pprint as pp
import os

if __name__ == '__main__':
    first_test = SentinelPass('S2A_MSIL2A_20200418T164901_N0214_R026_T16TCM_20200418T210937.SAFE',
                              './farm_simple.geojson')
    first_test.geotiff_to_png('ndvi')