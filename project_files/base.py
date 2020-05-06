'''
The purpose of this program is to use Sentinel-2 data to determine NDVI for the various paddocks around
the VoM grazing area. The final goal is to ingest the band 8 and band 4 data from Sentinel-2 satellites
and to turn that into 2 'products.' The first product is a KML/KMZ with a false color NDVI of the entire
VoM extent. The second/related project is to create/update a database with NDVI stats for each paddock.

Future growth opportunities include ingestion of the GoogleSheets information on herd movement and
production of graphs with herd movement and rainfall information included.
-------------------------------------------------------------------------------------------------------
Execution notes:
Installed package kml2geojson - gave cli option to convert kml to a geojson
Used geopandas to remove pushpin info wrote back to file with names/geometry as POLYGON Z


Deferred work:
Use the gml_transform script as a basis for assessing the downloaded jp2 for clouds before processing

--------------------------------------------------------------------------------------------------------
Structure:
- proj_class.py
-- Holds the SentinelPass class used to process downloaded imagery
-- Produces text files / images from the results of a pass





- queep.py
-- used for various admin tasks (likely not repeatable) in standing up this app
TODO:
- turn old paddock information into properly formatted GeoJSON info for each paddock


- database_setup.py
-- used for creation of an SQLite database to record/keep information on the farm
TODO:
- Create paddock table containing paddock name & GeoJSON outline
- Create tables for each paddock for recording stats


- base.py
-- foundational program for execution of required functions
TODO:

'''
import geopandas as gpd
import os
import shutil
import rasterio
from sentinelsat import SentinelAPI, read_geojson, geojson_to_wkt
import rasterio
import rasterio.mask
import os
import shutil
from zipfile import ZipFile

# Copernicus info
USER = 'bigusdeveloper'
PW = 'ZFknqZ3^44&&VGek'

def get_data():
    '''uses SentinelAPI to query for available products then downloads all products from query'''
    api = SentinelAPI(USER, PW, api_url='https://scihub.copernicus.eu/dhus')

    footprint = geojson_to_wkt(read_geojson('grazing.json'))
    products = api.query(footprint,
                         area_relation='Contains',
                         date=('20200401', '20200419'),
                         platformname='Sentinel-2',
                         processinglevel='Level-2A',
                         cloudcoverpercentage=(0, 75))

    # find most recent product - not currently doing anything
    products_gdf = api.to_geodataframe(products)
    products_gdf_sorted = products_gdf.sort_values(['ingestiondate'], ascending=[False])
    products_gdf_sorted = products_gdf_sorted.head(1)

    # currently implemented to download all products from query (be careful!!!)
    download_dict = api.download_all(products)
    '''(OrderedDict([('93a439d0-a01c-4b0c-8455-eedbce83e67a',
               {'id': '93a439d0-a01c-4b0c-8455-eedbce83e67a',
                'title': 'S2B_MSIL2A_20200420T163829_N0214_R126_T16TCM_20200420T210016',
                'size': 1179766201,
                'md5': '96AA0F65048AEB6C4405181A50A23A4C',
                'date': datetime.datetime(2020, 4, 20, 16, 38, 29, 24000),
                'footprint': 'POLYGON((-89.4281 42.344778566309515,-89.401886 42.427352942415745,-88.09686 42.44744302996699,-88.08002 41.458681613653354,-89.39395 41.438836285507165,-89.4281 42.344778566309515))',
                'url': "https://scihub.copernicus.eu/dhus/odata/v1/Products('93a439d0-a01c-4b0c-8455-eedbce83e67a')/$value",
                'Online': True,
                'Creation Date': datetime.datetime(2020, 4, 21, 3, 53, 12),
                'Ingestion Date': datetime.datetime(2020, 4, 21, 3, 51, 34, 635000),
                'path': './data/S2B_MSIL2A_20200420T163829_N0214_R126_T16TCM_20200420T210016.zip',
                'downloaded_bytes': 0}),
              ('df0e7ec5-8aa2-494d-81f4-8248e7cb3715',
               {'id': 'df0e7ec5-8aa2-494d-81f4-8248e7cb3715',
                'title': 'S2A_MSIL2A_20200418T164901_N0214_R026_T16TCM_20200418T210937',
                'size': 950415649,
                'md5': 'B67FD12948596CCBA710C097B197F184',
                'date': datetime.datetime(2020, 4, 18, 16, 49, 1, 24000),
                'footprint': 'POLYGON((-88.2193 42.44555793512965,-88.266266 42.32210347650357,-88.32178 42.17595021615731,-88.37698 42.029817915404905,-88.43179 41.88369968065968,-88.486176 41.73760294689875,-88.540375 41.59154583254291,-88.59244 41.4509420332511,-89.39395 41.438836285507165,-89.43118 42.42690168750588,-88.2193 42.44555793512965))',
                'url': "https://scihub.copernicus.eu/dhus/odata/v1/Products('df0e7ec5-8aa2-494d-81f4-8248e7cb3715')/$value",
                'Online': True,
                'Creation Date': datetime.datetime(2020, 4, 19, 4, 9, 19, 3000),
                'Ingestion Date': datetime.datetime(2020, 4, 19, 4, 7, 23, 613000),
                'path': './data/S2A_MSIL2A_20200418T164901_N0214_R026_T16TCM_20200418T210937.zip',
                'downloaded_bytes': 0})]),
 OrderedDict(),
 set())
'''

def unzip_files():
    '''Function should unzip the zipped downloads into the 'data' folder then remove the zipped file'''
    with ZipFile('./downloads/S2B_MSIL2A_20200420T163829_N0214_R126_T16TCM_20200420T210016.zip', 'r') as zipObj:
        zipObj.extractall('./data/') # don't need dirname as the top-level is a folder

    os.remove('./downloads/S2B_MSIL2A_20200420T163829_N0214_R126_T16TCM_20200420T210016.zip')

# TODO:


# TODO:


# TODO:



# TODO:




# TODO:



# TODO:



# TODO:



