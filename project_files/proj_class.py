import rasterio
import geopandas as gpd

class SentinelPass:
    def __init__(self, img_path: str, gjson_path: str):
        '''Initializes class with the path to a jp2 image and a GeoJSON set'''
        with rasterio.open(img_path) as img:
            self.img = img
        
            
    #TODO: mask image to simple square buffered around farm
    
    #TODO: compute NDVI for masked area
    
    #TODO: mask image for specific paddock
    
    #TODO: compute stats for a given paddock -> dict
        
    #TODO: transform 2D array to RGBA for writing PNG
    
    #TODO: connect to database
    
    #TODO: add NDVI data to database
    
    #TODO: write PNG into KML and return 
    
    
