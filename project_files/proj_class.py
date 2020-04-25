'''
This class will be used for processing data once it has been downloaded. The process of
querying the API for Sentinel data will be handled elsewhere.

The class will accept the paths for the b2, b4, and b8 images from a Sentinel-2 collect and compute the NDVI
and EVI for an area.

MVP:
Process single satellite pass into NDVI/EVI stats/info for each paddock individually

Follow-on capes:
Create KML with paddock data embedded.
Put results in database.
Save scaled down EVI and NDVI geotiffs
'''

import rasterio
import rasterio.mask
import geopandas as gpd
import numpy as np
from pprint import pprint as pp
import os
from datetime import datetime as dt


class SentinelPass:
    def __init__(self, safe_path: str,
                 gjson_path: str):
        """Initializes class with the paths b4 and b8 jp2's and GeoJSON path"""
        self.safe_path = safe_path
        self._find_files(self.safe_path)
        self.all_mask = gpd.read_file(gjson_path)
        self._pull_padded_box()
        self._evi_square()
        self._ndvi_square()

    def _find_files(self, safe_path: str):
        """Accepts the base path for a set of download files and pulls the string for each desired band"""
        for root, dirs, files in os.walk(safe_path):
            for file in files:
                if file.endswith("B02_10m.jp2"):
                    #print("Band 2 file " + os.path.join(root, file))
                    self.b2_path = os.path.join(root, file)
                elif file.endswith("B04_10m.jp2"):
                    #print("Band 4 file " + os.path.join(root, file))
                    self.b4_path = os.path.join(root, file)
                elif file.endswith("B08_10m.jp2"):
                    #print("Band 8 file " + os.path.join(root, file))
                    self.b8_path = os.path.join(root, file)


    def _pull_padded_box(self):
        """Pulls padded box info from the geojson file and sets attribute to an epsg:32616 geometry"""
        pad_geom = self.all_mask[self.all_mask.name == 'Padded box']  # access the geometry that's a box padded around the farm
        self.pad_geom_m = pad_geom.to_crs('epsg:32616')  # convert this geometry to the frame for


    def _ndvi_square(self):
        """parses the b4 and b8 data down to a simple square around the farm"""
        with rasterio.open(self.b4_path, 'r') as b4:
            b4_img, b4_transform = rasterio.mask.mask(b4, self.pad_geom_m.geometry, crop=True)
            b4_out_meta = b4.meta.copy()
            b4_out_meta.update({'driver': 'GTiff',
                                'height': b4_img.shape[1],
                                'width': b4_img.shape[2],
                                'transform': b4_transform})
            self.red = b4_img.astype(float)

        with rasterio.open(self.b8_path, 'r') as b8:
            b8_img, b8_transform = rasterio.mask.mask(b8, self.pad_geom_m.geometry, crop=True)
            self.nir = b8_img.astype(float)

        np.seterr(divide='ignore', invalid='ignore')
        self.ndvi = (self.nir - self.red) / (self.nir + self.red)
        b4_out_meta.update({'dtype': rasterio.float64})

        with rasterio.open('ndvi_masked.tiff', 'w', **b4_out_meta) as dest: # refactor to include datetime in name
            dest.write(self.ndvi.astype(rasterio.float64))


    def _evi_square(self):
        """parses the b4, b8, and b2 into an EVI array around the farm"""
        with rasterio.open(self.b4_path, 'r') as b4:
            b4_img, b4_transform = rasterio.mask.mask(b4, self.pad_geom_m.geometry, crop=True)
            b4_out_meta = b4.meta.copy()
            b4_out_meta.update({'driver': 'GTiff',
                                'height': b4_img.shape[1],
                                'width': b4_img.shape[2],
                                'transform': b4_transform})
            self.red = b4_img.astype(float) / 10000

        with rasterio.open(self.b8_path, 'r') as b8:
            b8_img, b8_transform = rasterio.mask.mask(b8, self.pad_geom_m.geometry, crop=True)
            self.nir = b8_img.astype(float) / 10000

        with rasterio.open(self.b2_path, 'r') as b2:
            b2_img, b2_transform = rasterio.mask.mask(b2, self.pad_geom_m.geometry, crop=True)
            self.blue = b2_img.astype(float) / 10000

        self.evi = 2.5 * (self.nir - self.red) / ((self.nir + 6.0 * self.red - 7.5 * self.blue) + 1.0)
        b4_out_meta.update({'dtype': rasterio.float64})

        with rasterio.open('evi_masked.tiff', 'w', **b4_out_meta) as dest: # refactor to include datetime info
            dest.write(self.evi.astype(rasterio.float64))


    def _paddock_mask(self, paddock_name: str):
        """Accepts paddock name and returns the UTM converted mask, epsg:32616"""
        # use gpd function '.to_crs('epsg:32616') to change the polygon to jp2 frame
        all_geom = gpd.read_file('farm_simple.geojson')
        paddock_geom = all_geom[all_geom.name == paddock_name]
        return paddock_geom.to_crs('epsg:32616')


    def paddock_stats(self, paddock_name: str, index: str = 'ndvi') -> dict:
        """accepts geodataframe for specific paddock and index ('ndvi' or 'evi') and computes statistics"""
        paddock_mask = self._paddock_mask(paddock_name)  # pull data from geojson and convert

        if index.lower() == 'evi':
            index_path = './evi_masked.tiff'
        elif index.lower() == 'ndvi':
            index_path = './ndvi_masked.tiff'
        else:
            print('Invalid index chosen. Chose either "evi" or "ndvi"')
            return {'result': 'Invalid index parameter provided'}


        with rasterio.open(index_path, 'r') as src:
            paddock_data, _ = rasterio.mask.mask(src, paddock_mask.geometry, crop=True)
            pdk_data_dict = {'index': index,
                paddock_name: {
                'max': np.nanmax(paddock_data),
                'min': np.nanmin(paddock_data),
                'mean': np.nanmean(paddock_data),
                'median': np.nanmedian(paddock_data),
                'std': np.nanstd(paddock_data),
                'var': np.nanvar(paddock_data),
                'pixels': np.count_nonzero(paddock_data)
            }}
        return pdk_data_dict


    def available_paddocks(self):
        """Processes the GeoJSON path in use by the instance and returns a list of names"""
        return list(self.all_mask['name'])


    def name_to_time(self, b2_name):
        split_name = b2_name.split('-')
        self.sense_date = dt.strftime(split_name[2], '%Y%m%dT%H%M%S')

    # TODO: use matlab cmap to color the square NDVI/EVI

    # TODO: connect to database

    # TODO: add NDVI data to database

    # TODO: write PNG into KML and return
