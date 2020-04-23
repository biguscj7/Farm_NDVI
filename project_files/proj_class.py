import rasterio
import geopandas as gpd

class SentinelPass:
    def __init__(self, img_path, gjson_path):
        '''Initializes class with the path to a jp2 image and a GeoJSON set'''
        with rasterio.open(img_path) as img:
            self.img = img
        with gpd.