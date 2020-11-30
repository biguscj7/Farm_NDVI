"""
This is a re-write of the original class for processing Sentinel 2 data into various indices. Upgrades include using
only geopandas (not kml2geojson) and masking the jp2 down to a smaller file before doing processing.

Improvements:
- Mask jp2 data before writing to geotiff
- Simplified application of kml
-- Use largest 'area' entry in geopandas?



Optional upgrades:
- Print the various paddock/outline names and allow the user to choose which one is used to trim the files

"""

from pathlib import Path, PurePath
import pandas as pd
from pprint import pprint as pp
import geopandas as gpd
from shapely.geometry import Polygon, box
from sentinelsat import SentinelAPI, geojson_to_wkt, read_geojson
import os
from datetime import date
from tabulate import tabulate
import rasterio
import rasterio.mask
from rasterio.warp import calculate_default_transform, reproject, Resampling
import fiona
import numpy as np
import os
from datetime import datetime as dt
from matplotlib import colors
from matplotlib import pyplot as plt
import shutil
import json


class SentinelPass:
    """
    Class is for handling a single set of images from Sentinel-2. Accepts a GeoDataFrame for processing, a database connection,
    and the folder name for a SAFE folder. A default f
    a GeoDataframe with paddock info, and a database connection
    """

    def __init__(
        self,
        farm_gdf,
        db_conn,
        safe_file,
        safe_dir="/Volumes/BIGUS_Storage/SAFE data/Unprocessed folders/",
    ):
        self.safe_folder = PurePath(safe_dir, safe_file)
        self.file_dict = self._find_file_path(self.safe_folder)
        self.sense_time = self._generate_sensing_time(safe_file)
        self.farm_gdf = farm_gdf
        self.buffered_geom = self.pull_buffered_geom()

    def _find_file_path(self, safe_folder: str) -> dict:
        """Accepts the base path for a set of download files and populates a dictionary with file paths for multiple items"""
        file_dict = {
            "B02_10m": None,
            "B04_10m": None,
            "B05_10m": None,
            "B08_10m": None,
            "B05_20m": None,
            "B8A_20m": None,
            "CLDPRB_20m": None,
            "TCI_10m": None,
            "WVP_10m": None,
            "AOT_10m": None,
        }

        for root, dirs, files in os.walk(safe_folder):
            for k, _ in file_dict.items():
                for file in files:
                    if file.endswith(f"{k}.jp2"):
                        file_dict.update({k: PurePath(root, file)})

        return file_dict

    def _generate_sensing_time(self, safe_file_name: str):
        """Parses name of files to create a datetime object for the sensing time"""
        date_str = safe_file_name.split("_")[2]
        return dt.strptime(date_str, "%Y%m%dT%H%M%S")

    def pull_buffered_geom(self):
        """Function to process the GeoDataFrame and return the geometry associated with the 'buffered' entry"""
        pass

    def generate_ndvi(self):
        """Open required band images and saves an NDVI geotiff for the bounding box"""
        # TODO: add bounding box info as parameter and use dictionary to generate a NDVI GEOtiff
        pass

    def generate_evi(self):
        """Uses the band data to generate an evi geotiff"""
        pass

    def generate_lai(self):
        """Uses the band data to generate an lai geotiff"""
        pass

    def generate_tci(self):
        """Uses the 3 color bands to generate a png file"""
        pass

    def _trim_band(self):
        """Uses the image limits to trim a band jp2 image, need to decide whether to store the image in temp or not"""
        # TODO: Use specific geometry trim the jp2 images
        pass

    def generate_aot(self):
        """Generates the geotiff info for aerosol optical thickness"""
        pass

    def generate_wvp(self):
        """Generates data from water vapor info"""
        pass


class FarmKML:
    """
    Class for dealing with KML files with paddock data and other geometries. Offers the option to define a
    geometry that includes all grazeable land. That geometry may include a single exclusion or hole.
    """

    def __init__(
        self,
        file_name: str = "votm_13_Oct_20.kml",
        outline: str = None,
        exclusion: str = None,
    ):
        self.path = Path(f"../KMZs/votm/{file_name}")
        self.init_gdf = self._parse_kml(self.path)
        self.plus_extents_gdf = self._get_max_extents()
        if outline:
            self.grazeable_gdf = self._create_grazeable(outline, exclusion)
        else:
            self.grazeable_gdf = self._create_grazeable(*self._get_outline_id())

    def _parse_kml(self, file_path):
        """Parses kml file and returns a Geodataframe"""
        gpd.io.file.fiona.drvsupport.supported_drivers["KML"] = "rw"

        return gpd.read_file(file_path, driver="KML")

    def _get_max_extents(self):
        """Generates a new dataframe that includes a buffered polygon around the limits of the polygons from the KML"""
        bound_df = self.init_gdf.total_bounds  # max x / y for all in gdf
        half_mile = 0.0083  # rough constant for 1/2 nm buffer latitude (using for longitude as well)
        buffer_box = box(
            bound_df[0] + half_mile,
            bound_df[1] + half_mile,
            bound_df[2] + half_mile,
            bound_df[3] + half_mile,
        )
        buffer_gdf = gpd.GeoDataFrame(
            {
                "Name": ["buffered"],
                "Description": "Max extents of dataframe with pad",
                "geometry": [buffer_box],
            },
            crs="EPSG:4326",
        )
        return pd.concat([self.init_gdf, buffer_gdf], ignore_index=True)

    def _create_grazeable(self, outline_name, exclusion_name):
        """Uses initial Geodataframe grazeable info to create a multi-poly with only grazeable land"""
        outline_poly = self.init_gdf[self.init_gdf.Name == outline_name][
            "geometry"
        ].values[0]
        if exclusion_name:
            exclusion_poly = self.init_gdf[self.init_gdf.Name == exclusion_name][
                "geometry"
            ].values[0]
            grazeable_poly = Polygon(outline_poly, holes=exclusion_poly)
            trimmed_gdf = self.plus_extents_gdf.loc[
                (self.plus_extents_gdf.Name != outline_name)
                & (self.plus_extents_gdf.Name != exclusion_name)
            ]

        else:
            grazeable_poly = outline_poly
            trimmed_gdf = self.plus_extents_gdf.loc[
                (self.plus_extents_gdf.Name != outline_name)
            ]

        grazeable_gdf = gpd.GeoDataFrame(
            {
                "Name": ["all_grazeable_land"],
                "Description": None,
                "geometry": [grazeable_poly],
            },
            crs="EPSG:4326",
        )

        return pd.concat([trimmed_gdf, grazeable_gdf], ignore_index=True)

    def _get_outline_id(self):
        """Presents gdf data to user to select outline and exclusion if a factor"""
        # TODO: Add stepping through the dataframe in chunks to avoid not seeing the prompt
        outline_index = int(
            input(
                f"\n{tabulate(self.plus_extents_gdf.iloc[:, 0:2], headers='keys')}\n"
                f"Enter your choice for outline of grazeable land: "
            )
        )
        exclusion_index = int(
            input(
                f"\n{tabulate(self.plus_extents_gdf.iloc[:, 0:2], headers='keys')}\n"
                f"Enter exclusion geometry if one exists, else enter '99': "
            )
        )

        outline_name = self.plus_extents_gdf.iloc[outline_index].Name

        if exclusion_index == 99:
            return outline_name, None
        else:
            exclusion_name = str(self.plus_extents_gdf.iloc[exclusion_index].Name)

            return outline_name, exclusion_name

    def tranform_crs(self, new_crs: str):
        """Accepts a new crs and returns the transformed Geodataframe"""
        return self.plus_extents_gdf.to_crs(new_crs)

    def print_kml(self, printable_gdf):
        """Prints the Geopandas data frame information nicely for review"""
        pp(printable_gdf)


def sentinel_api(geojson):
    """Testing API inclusion"""
    # TODO: rework this to query the user for the geometry name to use for api query
    api = SentinelAPI(
        os.getenv("SENTINEL_LOGIN"),
        os.getenv("SENTINEL_PW"),
        "https://scihub.copernicus.eu/apihub/",
    )
    footprint = geojson_to_wkt(geojson)

    products = api.query(
        footprint,
        date=(date(2020, 6, 1), date(2020, 8, 1)),
        platformname="Sentinel-2",
        producttype="S2MSI2A",
        area_relation="Contains",
    )
    prod_df = api.to_dataframe(products)
    """['title', 'link', 'link_alternative', 'link_icon', 'summary',
       'beginposition', 'endposition', 'ingestiondate', 'orbitnumber',
       'relativeorbitnumber', 'vegetationpercentage', 'notvegetatedpercentage',
       'waterpercentage', 'unclassifiedpercentage',
       'mediumprobacloudspercentage', 'highprobacloudspercentage',
       'snowicepercentage', 'cloudcoverpercentage', 'level1cpdiidentifier',
       'gmlfootprint', 'footprint', 'format', 'processingbaseline',
       'platformname', 'filename', 'instrumentname', 'instrumentshortname',
       'size', 's2datatakeid', 'producttype', 'platformidentifier',
       'orbitdirection', 'platformserialidentifier', 'processinglevel',
       'identifier', 'uuid']"""

    pp(prod_df.cloudcoverpercentage)


if __name__ == "__main__":
    votm = FarmKML()
    # print(votm.grazeable_gdf)
    # buff_str = votm.plus_extents_gdf[votm.plus_extents_gdf.Name == 'buffered'].geometry.to_json()
    # buff_json = json.loads(buff_str)
    # buff_json = buffered_ser.to_json()
    # sentinel_api(buff_json)
