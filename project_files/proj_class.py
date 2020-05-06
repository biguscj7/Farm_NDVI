'''
This class will be used for processing data once it has been downloaded. The process of
querying the API for Sentinel data will be handled elsewhere.

The class will accept the path for a SAFE folder and then extract the b2, b4, and b8 images from a Sentinel-2 collect
and compute the NDVI and EVI for an area.

MVP:
Process single satellite pass into NDVI/EVI stats/info for each paddock individually

Follow-on capes:
Create KML with paddock data embedded.
Put results in database.
'''

import rasterio
import rasterio.mask
from rasterio.warp import calculate_default_transform, reproject, Resampling
import geopandas as gpd
import numpy as np
from pprint import pprint as pp
import os
from datetime import datetime as dt
from matplotlib import colors
from matplotlib import pyplot as plt
import shutil
import json


class SentinelPass:
    def __init__(self, safe_path: str,
                 farm: str):
        """Initializes class with the Sentinel SAFE folder path and GeoJSON path"""
        self.safe_path = safe_path
        self._find_files(self.safe_path)
        self.farm = farm
        self._name_to_time(self.b2_fn)
        if self.farm == 'votm':
            self._all_mask = gpd.read_file('./KMZs/votm/farm_simple.geojson')
        else:
            self._all_mask = gpd.read_file('./KMZs/brass/brass_farm.geojson')
        self._pull_padded_box()
        if f"ndvi_{self.sense_date.strftime('%Y%m%d')}.tiff" not in os.listdir(f'./geotiffs/{farm}/'):
            for k, v in self.band_dict.items():
                self._reproject_wgs84(k, v)
            self._ndvi_square()
            self._evi_square()
            self._color_square()
            self._cloud_processing()
            self._write_cloud_stats()
            self._tmp_img_cleanup()

    def _find_files(self, safe_folder: str) -> dict:
        """Accepts the base path for a set of download files and populates a dictionary with file paths for multiple items"""
        self.band_dict = {
            'band02': '',
            'band03': '',
            'band04': '',
            'band08': '',
            'clouds': ''
        }

        for root, dirs, files in os.walk(f'../data/{safe_folder}'):
            for file in files:
                if file.endswith("B02_10m.jp2"):
                    self.band_dict['band02'] = os.path.join(root, file)
                    self.b2_fn = file # pulls filename rather than path for parsing datetime
                elif file.endswith("B03_10m.jp2"):
                    self.band_dict['band03'] = os.path.join(root, file)
                elif file.endswith("B04_10m.jp2"):
                    self.band_dict['band04'] = os.path.join(root, file)
                elif file.endswith("B08_10m.jp2"):
                    self.band_dict['band08'] = os.path.join(root, file)
                elif file.endswith("PRB_20m.jp2"):
                    self.band_dict['clouds'] = os.path.join(root, file)

    def _pull_padded_box(self):
        """Pulls padded box info from the geojson file"""
        self.pad_geom = self._all_mask[self._all_mask.name == f'{self.farm} farm padded']

    # TODO: Implement delete of data file once bands have been pulled
    def _reproject_wgs84(self, band, file_path):
        """Reprojects jp2 into WGS84 crs and writes as GeoTIFF prior to masking file"""

        dst_crs = 'epsg:4326'

        with rasterio.open(file_path, 'r') as src:
            transform, width, height = calculate_default_transform(
                src.crs, dst_crs, src.width, src.height, *src.bounds)
            kwargs = src.meta.copy()
            kwargs.update({
                'crs': dst_crs,
                'transform': transform,
                'width': width,
                'height': height,
                'driver': 'GTiff'
            })

            with rasterio.open(f'./tmp_img/{band}.tiff', 'w', **kwargs) as dst:
                reproject(source=rasterio.band(src, 1),
                          destination=rasterio.band(dst, 1),
                          src_transform=src.transform,
                          src_crs=src.crs,
                          dst_transform=transform,
                          dst_crs=dst_crs,
                          resampling=Resampling.nearest)

    # TODO: Refactor for use of dictionary to track filenames through initialization
    def _ndvi_square(self):
        """parses the b4 and b8 data down to a simple square around the farm"""
        with rasterio.open('./tmp_img/band04.tiff', 'r') as b4:
            b4_img, b4_transform = rasterio.mask.mask(b4, self.pad_geom.geometry, crop=True)
            b4_out_meta = b4.meta.copy()
            b4_out_meta.update({'driver': 'GTiff',
                                'height': b4_img.shape[1],
                                'width': b4_img.shape[2],
                                'transform': b4_transform})
            self.red = b4_img.astype(float)

        with rasterio.open('./tmp_img/band08.tiff', 'r') as b8:
            b8_img, b8_transform = rasterio.mask.mask(b8, self.pad_geom.geometry, crop=True)
            self.nir = b8_img.astype(float)

        np.seterr(divide='ignore', invalid='ignore')
        self.ndvi = (self.nir - self.red) / (self.nir + self.red)
        b4_out_meta.update({'dtype': rasterio.float64})

        with rasterio.open(self.ndvi_gtf_name, 'w', **b4_out_meta) as dest:
            dest.write(self.ndvi.astype(rasterio.float64))

    def _evi_square(self):
        """parses the b4, b8, and b2 into an EVI array around the farm"""
        with rasterio.open('./tmp_img/band04.tiff', 'r') as b4:
            b4_img, b4_transform = rasterio.mask.mask(b4, self.pad_geom.geometry, crop=True)
            b4_out_meta = b4.meta.copy()
            b4_out_meta.update({'driver': 'GTiff',
                                'height': b4_img.shape[1],
                                'width': b4_img.shape[2],
                                'transform': b4_transform})
            self.red = b4_img.astype(float) / 10000

        with rasterio.open('./tmp_img/band08.tiff', 'r') as b8:
            b8_img, b8_transform = rasterio.mask.mask(b8, self.pad_geom.geometry, crop=True)
            self.nir = b8_img.astype(float) / 10000

        with rasterio.open('./tmp_img/band02.tiff', 'r') as b2:
            b2_img, b2_transform = rasterio.mask.mask(b2, self.pad_geom.geometry, crop=True)
            self.blue = b2_img.astype(float) / 10000

        self.evi = 2.5 * (self.nir - self.red) / ((self.nir + 6.0 * self.red - 7.5 * self.blue) + 1.0)
        b4_out_meta.update({'dtype': rasterio.float64})

        with rasterio.open(self.evi_gtf_name, 'w', **b4_out_meta) as dest:
            dest.write(self.evi.astype(rasterio.float64))

    def _color_square(self):
        """parses the b2, b3, and b4 into an full color array around the farm"""
        with rasterio.open('./tmp_img/band04.tiff', 'r') as b4:
            b4_img, b4_transform = rasterio.mask.mask(b4, self.pad_geom.geometry, crop=True)
            b4_out_meta = b4.meta.copy()
            b4_out_meta.update({'driver': 'GTiff',
                                'height': b4_img.shape[1],
                                'width': b4_img.shape[2],
                                'transform': b4_transform,
                                'count': 3})
            self.red = b4_img

        with rasterio.open('./tmp_img/band03.tiff', 'r') as b3:
            b3_img, _ = rasterio.mask.mask(b3, self.pad_geom.geometry, crop=True)
            self.green = b3_img

        with rasterio.open('./tmp_img/band02.tiff', 'r') as b2:
            b2_img, _ = rasterio.mask.mask(b2, self.pad_geom.geometry, crop=True)
            self.blue = b2_img

        with rasterio.open(self.color_gtf_name, 'w', **b4_out_meta) as dest:
            dest.write(b4_img[0], 1)
            dest.write(b3_img[0], 2)
            dest.write(b2_img[0], 3)

    def _cloud_processing(self):
        """Will process the cloud masking data to assess the likelihood of clouds"""
        farm_mask = self._all_mask[self._all_mask.name == f'{self.farm} farm padded']

        with rasterio.open('./tmp_img/clouds.tiff', 'r') as cloud:
            cloud_data, _ = rasterio.mask.mask(cloud, farm_mask.geometry, crop=True, nodata=101)

        cloud_data_mask = cloud_data < 101

        cld_arr = cloud_data[cloud_data_mask] # apply mask to get 1D array for analysis

        self.cloud_dict = {'max': int(np.max(cld_arr)),
                           'num_cld_pixels': int(np.count_nonzero(cld_arr)),
                           'pixels': int(np.size(cld_arr)),
                           'median': int(np.median(cld_arr)),
                           '25_percentile': int(np.percentile(cld_arr, 25)),
                           '50_percentile': int(np.percentile(cld_arr, 50)),
                           '75_percentile': int(np.percentile(cld_arr, 75))}

    def _tmp_img_cleanup(self):
        """Deletes all Currently expedient hardcoded delete of """
        for fn in [x for x in os.listdir('./tmp_img/')]:
            os.remove(f'./tmp_img/{fn}')

    def _name_to_time(self, b2_name: str):
        split_name = b2_name.split('_')
        self.sense_date = dt.strptime(split_name[1], '%Y%m%dT%H%M%S')
        self.ndvi_gtf_name = f"./geotiffs/{self.farm}/ndvi_{self.sense_date.strftime('%Y%m%d')}.tiff"
        self.evi_gtf_name = f"./geotiffs/{self.farm}/evi_{self.sense_date.strftime('%Y%m%d')}.tiff"
        self.color_gtf_name = f"./geotiffs/{self.farm}/color_{self.sense_date.strftime('%Y%m%d')}.tiff"

    def _write_cloud_stats(self):
        with open(f"./stats/{self.farm}/{self.sense_date.strftime('%Y%m%d')}_cloud.json", "w") as outfile:
            json.dump(self.cloud_dict, outfile)

    # TODO: Refactor to account for new naming convention for files
    def paddock_stats(self, index: str = 'ndvi', paddock_name: str = 'Farm boundary') -> dict:
        """accepts geodataframe for specific paddock and index ('ndvi' or 'evi') and computes statistics, and writes"""
        paddock_mask = self._all_mask[self._all_mask.name == paddock_name]

        if index.lower() == 'evi':
            index_path = f"./geotiffs/{self.farm}/evi_{self.sense_date.strftime('%Y%m%d')}.tiff"
        elif index.lower() == 'ndvi':
            index_path = f"./geotiffs/{self.farm}/ndvi_{self.sense_date.strftime('%Y%m%d')}.tiff"
        else:
            print('Invalid index chosen. Chose either "evi" or "ndvi"')
            return {'result': 'Invalid index parameter provided'}

        with rasterio.open(index_path, 'r') as src:
            paddock_data, _ = rasterio.mask.mask(src,
                                         paddock_mask.geometry,
                                         crop=True,
                                         nodata=-2) # chose not to use all_touched=True option

        data_mask = paddock_data >= -1
        simple_data = paddock_data[data_mask]

        pdk_data_dict = {'index': index,
                         paddock_name: {
                             'max': np.max(simple_data),
                             'min': np.min(simple_data),
                             'mean': np.mean(simple_data),
                             'median': np.median(simple_data),
                             'std': np.std(simple_data),
                             'var': np.var(simple_data),
                             'pixels': np.size(simple_data),
                             '25_percent': np.percentile(simple_data, 25),
                             '50_percent': np.percentile(simple_data, 50),
                             '75_percent': np.percentile(simple_data, 75),
                             }}

        for k, v in pdk_data_dict[paddock_name].items():
            pdk_data_dict[paddock_name].update({k: float(v)})

        with open(f"./stats/{self.farm}/{self.sense_date.strftime('%Y%m%d')}_{paddock_name}_{index}.json", "w") as outfile:
            json.dump(pdk_data_dict, outfile)

        return pdk_data_dict # kind of a waste to write and return as well, for development only

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

        ax.imshow(img_norm, cmap='RdYlGn')
        plt.savefig(f"./pics/{self.farm}/{index.lower()}_{self.sense_date.strftime('%Y%m%d')}.png", transparent=True)
        plt.close()

    # TODO: Function to implement logic checking for clouds in FOV - seems like some non-visible clouds affect indices
    # Logic inputs - count of cloud estimated pixels on 60m jp2, mean values for both EVI + NDVI (which extreme?)
    # Where to implement result? Dictionary for each paddock? Depends on database structure


    # TODO: add NDVI data to database

    # TODO: write PNG into KML and return

