import rasterio
from rasterio.plot import show
import os
import time
import json

if __name__ == '__main__':
    pic_dict = {}
    files = [fn for fn in os.listdir('../geotiffs/votm/') if fn.startswith('color')]
    for file in files:
        timestamp = file.split('_')[1].split('.')[0]
        with rasterio.open(f'../geotiffs/votm/{file}', 'r') as src:
            rasterio.plot.show(src)
            cld_pct = input("Please enter percentage of clouds:")
        pic_dict.update({timestamp: cld_pct})

    file_content = json.dumps(pic_dict)
    with open('../stats/votm/cloud.json', 'w') as outfile:
        outfile.write(file_content)