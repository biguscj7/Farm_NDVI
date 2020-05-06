from proj_class import SentinelPass
import numpy as np
from pprint import pprint as pp
import os

if __name__ == '__main__':
    path_str = 'S2B_MSIL2A_20200503T164839_N0214_R026_T16TCM_20200503T211237.SAFE'

    brass = SentinelPass(path_str, 'brass')
    brass.geotiff_to_png('ndvi')
    brass.paddock_stats('ndvi')
