import pytest
import fiona
import geopandas as gpd

from Farm_NDVI.project_files.scripts.sentinel2 import FarmKML

def test_farmKML_crs():
    test_farm = FarmKML('input.kml')
    assert test_farm.plus_extents_gdf.crs == "EPSG:4326"
