import rasterio
from rasterio.plot import show

if __name__ == '__main__':
    with rasterio.open('../geotiffs/votm/color_20191006T1651.tiff', 'r') as src:
        rasterio.plot.show(src)