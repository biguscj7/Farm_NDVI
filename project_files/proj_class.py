'''
This class will be used for processing data once it has been downloaded. The process of
querying the API for Sentinel data will be handles elsewhere.

The class will accept the paths for the b4 and b8 images from a pass as well as an sqlite
database name. It will allow the user to process the images to return NDVI info for each
paddock.

MVP:
Process single satellite pass into NDVI stats/info for each paddock individually

Follow-on capes:
Create KML with paddock data embedded.
'''


import rasterio
import geopandas as gpd
import numpy as np
from pprint import pprint as pp
import os

class SentinelPass:
    def __init__(self, b4_path: str,
                 b8_path: str,
                 gjson_path: str):
        """Initializes class with the paths b4 and b8 jp2's and GeoJSON path"""
        self.b4_path = b4_path
        self.b8_path = b8_path
        self.all_mask = gpd.read_file(gjson_path)


    def _pull_padded_box(self):
        """Pulls padded box info from the geojson file and sets attribute to an epsg:32616 geometry"""
        all_geom = gpd.read_file('farm_simple.geojson') # read the polygon geometries for the farm
        pad_geom = all_geom[all_geom.name == 'Padded box'] # access the geometry that's a box padded around the farm
        self.pad_geom_m = pad_geom.to_crs('epsg:32616') # convert this geometry to the frame for


    #TODO: mask image to simple square buffered around farm
    def _ndvi_square(self):
        """parses the b4 and b8 data down to a simple square around the farm"""
        with rasterio.open(self.b4_path, 'r') as b4:
            b4_img, b4_transform = rasterio.mask.mask(b4, self.pad_geom_m.geometry, crop=True)
            b4_out_meta = self.b4.meta.copy()
            b4_out_meta.update({'driver': 'GTiff',
                                'height': b4_img.shape[1],
                                'width': b4_img.shape[2],
                                'transform': b4_transform})
            self.red = b4_img.astype(float)

        with rasterio.open(self.b8_path, 'r') as b8:
            b8_img, b8_transform = rasterio.mask.mask(b8, self.pad_geom_m.geometry, crop=True)
            self.nir = b8_img.astype(float)

        self.ndvi = (self.nir - self.red) / (self.nir + self.red)
        b4_out_meta.update({'dtype': rasterio.float64})

        with rasterio.open('NDVI_masked.tiff', 'w', **b4_out_meta) as dest:
            dest.write(ndvi.astype(rasterio.float64))

    def _paddock_mask(self, paddock_name: str):
        """Accepts paddock name and returns the UTM converted mask, epsg:32616"""
        # use gpd function '.to_crs('epsg:32616') to change the polygon to jp2 frame
        all_geom = gpd.read_file('farm_simple.geojson')
        paddock_geom = all_geom[all_geom.name == paddock_name]
        return paddock_geom.to_crs('epsg:32616')


    def paddock_stats(self, paddock_name: str) -> dict:
        """accepts geodataframe for specific paddock and computes statistics for the values"""
        paddock_mask = _paddock_mask(paddock_name) # pull data from geojson and convert

        with rasterio.open('NDVI_masked.tiff', 'r') as src:
            paddock_data, _ = rasterio.mask.mask(src, paddock_mask.geometry, crop=True)
            pdk_data_dict = {paddock_name:{
                'max': np.nanmax(paddock_data),
                'min': np.nanmin(paddock_data),
                'mean': np.nanmean(paddock_data),
                'median': np.nanmedian(paddock_data),
                'std': np.nanstd(paddock_data),
                'var': np.nanvar(paddock_data),
                'pixels': np.count_nonzero(~np.isnan(paddock_data))
            }}
        return pdk_data_dict

    #TODO: transform 2D array to RGB for writing PNG in desired colors
    
    #TODO: connect to database
    
    #TODO: add NDVI data to database
    
    #TODO: write PNG into KML and return