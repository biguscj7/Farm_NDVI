import geopandas as gpd

def geojson_simplify(in_file, out_file):
    '''reads in geojson file and simplifies it to only name and geometry then writes it to file
    provided an string for filename to open and filename to write'''
    farm = gpd.read_file(in_file)
    farm_simp = farm[['name', 'geometry']]
    farm_simp.to_file(out_file, driver='GeoJSON')