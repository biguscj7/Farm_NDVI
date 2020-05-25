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
            farm_visible = input("Is the farm 100% visible? (y/n): ")
            vis_moisture = input("Is there visible moisture that may affect readings? (y/n): ")
            if farm_visible.lower() == 'n':
                e18 = input("Are paddocks in the east 18 clear? (y/n): ")
                hay_field = input("Are paddocks in the old hay field clear? (y/n): ")
                cedar_hill = input("Are paddocks on cedar hill clear (y/n): ")
            else:
                e18, hay_field, cedar_hill = 'y', 'y', 'y'

        pic_dict.update({timestamp: {'farm_visible': farm_visible,
                                     'vis_moisture': vis_moisture,
                                     'e18': e18,
                                     'hay_field': hay_field,
                                     'cedar_hill': cedar_hill}})

    for k, v in pic_dict.items():
        for x, y in v.items():
            if y == 'y':
                pic_dict[k][x] = True
            elif y == 'n':
                pic_dict[k][x] = False

    file_content = json.dumps(pic_dict)
    with open('../stats/votm/cloud.json', 'w') as outfile:
        outfile.write(file_content)