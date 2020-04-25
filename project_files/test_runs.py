from proj_class import SentinelPass
import numpy as np
from pprint import pprint as pp
import os

first_test = SentinelPass('../data/S2A_MSIL2A_20200418T164901_N0214_R026_T16TCM_20200418T210937.SAFE',
                          './farm_simple.geojson')

if __name__ == '__main__':
    print(first_test.paddock_stats('Paddock 14'))