from proj_class import SentinelPass
import numpy as np
import pandas as pd
from pprint import pprint as pp
import os

if __name__ == '__main__':
    path_str = 'S2B_MSIL2A_20200513T164839_N0214_R026_T16TCM_20200513T224015.SAFE'

    votm = SentinelPass(path_str, 'votm')
    votm.gather_pdk_stats('ndvi')
    votm.gather_pdk_stats('evi')
    votm.gather_pdk_stats('lai')