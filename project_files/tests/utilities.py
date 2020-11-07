import fiona
import geopandas as gpd
from shapely.geometry import polygon, box



simple_box = box(-89, 42, -88, 43)
inner_box = box(-88.75, 42.25, -88.25, 42.75)

new_gdf = gpd.GeoDataFrame({'Name': ['Grazeable outer', 'Non-grazeable inner'],
                  'Description': None,
                  'geometry': [simple_box, inner_box]}, crs="EPSG:4326")

fiona.supported_drivers['KML'] = 'rw'

new_gdf.to_file('input.kml', driver='KML')

if __name__ == '__main__':
    pass