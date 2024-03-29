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
from matplotlib import colors
from matplotlib import pyplot as plt


class SentinelPass:
    def __init__(self, safe_path: str,
                 gjson_path: str):
        """Initializes class with the paths b4 and b8 jp2's and GeoJSON path"""
        self.safe_path = safe_path
        self._find_files(self.safe_path)
        self._name_to_time(self.b2_fn)
        self._all_mask = gpd.read_file(gjson_path)
        self._pull_padded_box()
        self._evi_square()
        self._ndvi_square()

    def _find_files(self, safe_folder: str):
        """Accepts the base path for a set of download files and pulls the string for each desired band"""
        for root, dirs, files in os.walk(f'../data/{safe_folder}'):
            for file in files:
                if file.endswith("B02_10m.jp2"):
                    # print("Band 2 file " + os.path.join(root, file))
                    self.b2_path = os.path.join(root, file)
                    self.b2_fn = file
                elif file.endswith("B04_10m.jp2"):
                    # print("Band 4 file " + os.path.join(root, file))
                    self.b4_path = os.path.join(root, file)
                elif file.endswith("B08_10m.jp2"):
                    # print("Band 8 file " + os.path.join(root, file))
                    self.b8_path = os.path.join(root, file)

    def _pull_padded_box(self):
        """Pulls padded box info from the geojson file and sets attribute to an epsg:32616 geometry"""
        pad_geom = self._all_mask[
            self._all_mask.name == 'Padded box']  # access the geometry that's a box padded around the farm
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

        self.ndvi_gtf_name = f"./pics/ndvi_{self.sense_date.strftime('%Y%m%d')}.tiff"
        with rasterio.open(self.ndvi_gtf_name, 'w', **b4_out_meta) as dest:
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

        self.evi_gtf_name = f"./pics/evi_{self.sense_date.strftime('%Y%m%d')}.tiff"
        with rasterio.open(self.evi_gtf_name, 'w', **b4_out_meta) as dest:
            dest.write(self.evi.astype(rasterio.float64))

    def _paddock_mask(self, paddock_name: str):
        """Accepts paddock name and returns the UTM converted mask, epsg:32616"""
        # use gpd function '.to_crs('epsg:32616') to change the polygon to jp2 frame
        all_geom = gpd.read_file('../project_files/KMZs/votm/farm_simple')
        paddock_geom = all_geom[all_geom.name == paddock_name]
        return paddock_geom.to_crs('epsg:32616')

    def _name_to_time(self, b2_name: str):
        split_name = b2_name.split('_')
        self.sense_date = dt.strptime(split_name[1], '%Y%m%dT%H%M%S')

    def paddock_stats(self, paddock_name: str, index: str = 'ndvi') -> dict:
        """accepts geodataframe for specific paddock and index ('ndvi' or 'evi') and computes statistics"""
        paddock_mask = self._paddock_mask(paddock_name)  # pull data from geojson and convert

        if index.lower() == 'evi':
            index_path = './pics/evi_masked.tiff'
        elif index.lower() == 'ndvi':
            index_path = './pics/ndvi_masked.tiff'
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
        return list(self._all_mask['name'])

    def geotiff_to_png(self, index: str):
        """This method will accept the index (ndvi/evi) and process the geotiff image to produce a masked and transparent
        image in png format."""
        if index.lower() == 'ndvi':
            with rasterio.open(self.ndvi_gtf_name, 'r') as src:
                img_arr = src.read(1)
        elif index.lower() == 'evi':
            with rasterio.open(self.evi_gtf_name, 'r') as src:
                img_arr = src.read(1)
        else:
            return "You have not selected a valid index."

        img_arr_prep = np.nan_to_num(img_arr, nan=-1.0)
        img_norm = (img_arr_prep + 1.0) / 2.0  # normalizes array from range -1,1 to range 0,1


        # custom colordict for transparent values of a segmented 3 color line
        cdict = {'red':     ((0.0, 0.65, 0.65),
                            (0.25, 0.97, 0.97),
                            (0.5, 1.0, 1.0),
                            (0.75, 0.53, 0.53),
                            (1.0, 0.0, 0.0)),
                 'green':   ((0.0, 0.0, 0.0),
                            (0.25, 0.55, 0.55),
                            (0.5, 1.0, 1.0),
                            (0.75, 0.80, 0.80),
                            (1.0, 0.41, 0.41)),
                 'blue':    ((0.0, 0.15, 0.15),
                            (0.25, 0.32, 0.32),
                            (0.5, 0.75, 0.75),
                            (0.75, 0.4, 0.4),
                            (1.0, 0.22, 0.22)),
                 'alpha':   ((0.0, 0.0, 0.0),
                            (0.02, 0.0, 1.0),
                            (0.03, 1.0, 1.0),
                            (1.0, 1.0, 1.0))}
        mymap = colors.LinearSegmentedColormap('mymap', cdict)

        # prepping template to save png with transparency and no border info
        fig = plt.figure()
        ax = plt.Axes(fig, [0., 0., 1., 1.])
        ax.set_axis_off()
        ax.margins(0)
        fig.add_axes(ax)

        ax.imshow(img_norm, cmap=mymap)
        plt.savefig(f"./pics/{index.lower()}_{self.sense_date.strftime('%Y%m%d')}.png", transparent=True)
        plt.close()

    # TODO: connect to database

    # TODO: add NDVI data to database

    # TODO: write PNG into KML and return
