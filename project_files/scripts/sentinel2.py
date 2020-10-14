'''
This is a re-write of the original class for processing Sentinel 2 data into various indices. Upgrades include using
only geopandas (not kml2geojson) and masking the jp2 down to a smaller file before doing processing.

Improvements:
- Mask jp2 data before writing to geotiff
- Simplified application of kml
-- Use largest 'area' entry in geopandas?



Optional upgrades:
- Print the various paddock/outline names and allow the user to choose which one is used to trim the files

'''


from pathlib import Path
import rasterio
import rasterio.mask
from rasterio.warp import calculate_default_transform, reproject, Resampling
import fiona
import geopandas as gpd
from shapely.geometry import Polygon
import numpy as np
import pandas as pd
from pprint import pprint as pp
import os
from datetime import datetime as dt
from matplotlib import colors
from matplotlib import pyplot as plt
import shutil
import json

class SentinelPass:
    '''Class is for handling a single set of images from Sentinel-2'''
    def __init__(self, file_path, image_limits):
        '''Accept the file path for a "SAFE" folder and the lateral/vertical max/min'''
        pass

    def _generate_sensing_time(self):
        '''Parses name of files to create a datetime object for the sensing time'''
        pass

    def _trim_bands(self):
        '''Uses the image limits to trim a band jp2 image, need to decide whether to store the image in temp or not'''
        pass

    def generate_ndvi(self):
        '''Uses the band images to generate an ndvi geotiff'''
        pass

    def generate_evi(self):
        '''Uses the band data to generate an evi geotiff'''
        pass

    def generate_lai(self):
        '''Uses the band data to generate an lai geotiff'''
        pass

    def generate_tci(self):
        '''Uses the 3 color bands to generate a png file'''
        pass



class FarmKML:
    '''Class for dealing with KML files with paddock data and other geometries. Intend to internally use geopandas
    dataframes.'''

    def __init__(self, file_name: str):
        self.path = Path(f'../KMZs/votm/{file_name}')
        self.base_gdf = self._parse_kml(self.path)
        self.base_buffered_gdf = self.get_max_extents()

    def _parse_kml(self, file_path):
        '''Parses kml file and returns a Geodataframe'''
        gpd.io.file.fiona.drvsupport.supported_drivers['KML'] = 'rw'

        return gpd.read_file(file_path, driver="KML")

    def get_max_extents(self):
        '''Generates a new dataframe that includes a buffered polygon around the limits of the polygons from the KML'''
        bound_df = self.base_gdf.total_bounds # max x / y for all in gdf
        half_mile = 0.0083 # rough constant for 1/2 nm buffer latitude (using for longitude as well)
        minx = bound_df[0] + half_mile
        miny = bound_df[1] + half_mile
        maxx = bound_df[2] + half_mile
        maxy = bound_df[3] + half_mile
        bound_poly = Polygon([(minx, miny), (maxx, miny), (maxx, maxy), (minx, maxy), (minx, miny)])
        buffer_gdf = gpd.GeoDataFrame({'Name': ['buffered'], 'Description': None, 'geometry': [bound_poly]},
                                      crs="EPSG:4326")
        return pd.concat([self.base_gdf, buffer_gdf], ignore_index=True)


    def tranform_crs(self, new_crs: str):
        '''Accepts a new crs and returns the transformed Geodataframe'''
        return self.base_buffered_gdf.to_crs(new_crs)

    def print_kml(self, printable_gdf):
        '''Prints the Geopandas data frame information nicely for review'''
        pp(printable_gdf)

if __name__ == '__main__':
    votm = FarmKML('votm_13_Oct_20.kml')
    meters_gdf = votm.tranform_crs('epsg:32616')
    pp(meters_gdf)