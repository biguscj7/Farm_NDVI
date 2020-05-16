from proj_class import SentinelPass
import numpy as np
import pandas as pd
from pprint import pprint as pp
import os

if __name__ == '__main__':
    path_str = 'S2B_MSIL2A_20200513T164839_N0214_R026_T16TCM_20200513T224015.SAFE'

    votm = SentinelPass(path_str, 'votm')
    votm.geotiff_to_png('ndvi')
    votm.geotiff_to_png('evi')
    votm.paddock_stats('ndvi')
    votm.paddock_stats('evi')

    stat_paddocks = ['Paddock 1', 'Paddock 2', 'Paddock 3', 'Paddock 4', 'Paddock 5',
                     'Paddock 6', 'Paddock 7', 'Paddock 8', 'Paddock 9', 'Paddock 10',
                     'Paddock 11', 'Paddock 12', 'Paddock 13', 'Paddock 14', 'Paddock 15',
                     'Paddock 16', 'Paddock 17', 'Paddock 18', 'Paddock 19', 'Paddock 20',
                     'Paddock 21', 'Paddock 22', 'Paddock 23', 'East 18 North', 'East 18 South']

    stat_index = 'ndvi'




    '''
    with open(f'./stats/votm/{votm.sense_datetime.strftime("%Y%m%d")}_{stat_index}.txt', 'w') as stat_file:
        stat_file.write(f"{'Paddock':>20}{'Max':^15}{'Mean':^10}{'Median':^10}{'Min':^10}{'Pixels':^10}\n")
        stat_file.write(f"{'-':-^75}\n")

    for paddock in stat_paddocks:
        pdk_stats = votm.paddock_stats(stat_index, paddock)
        with open(f'./stats/votm/{votm.sense_datetime.strftime("%Y%m%d")}_{stat_index}.txt', 'a') as stat_file:
            stat_file.write(f"{paddock:>20}{pdk_stats[paddock]['max']:^15.3f}{pdk_stats[paddock]['mean']:^10.3f}"
                            f"{pdk_stats[paddock]['median']:^10.3f}{pdk_stats[paddock]['min']:^10.3f}"
                            f"{pdk_stats[paddock]['pixels']:^10.0f}\n")'''