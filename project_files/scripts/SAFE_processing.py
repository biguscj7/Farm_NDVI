from proj_class import SentinelPass
import os

if __name__ == '__main__':
    for foldername in os.listdir('/Volumes/BIGUS_Storage/SAFE data/Unprocessed folders/'):
        if foldername.endswith('SAFE'):
            path_str = foldername
            votm = SentinelPass(path_str, 'votm')
            votm.gather_pdk_stats('ndvi')
            votm.gather_pdk_stats('evi')
            votm.gather_pdk_stats('lai')
            votm.geotiff_to_png('ndvi')
            votm.geotiff_to_png('evi')