import rasterio
from rasterio.plot import show
import os
import time
import json


def get_current_data():
    """Retrieve current cloud data from cloud.json file"""
    with open('../stats/votm/cloud.json', 'r') as cld_file:
        return json.load(cld_file)


def filter_file_list(curr_list):
    """Filter out entries from current directory list if already present"""
    all_list = [fn for fn in os.listdir('../geotiffs/votm/') if fn.startswith('color')]
    for timestamp in curr_list:
        for x in range(len(all_list) - 1, -1, -1):
            if timestamp in all_list[x]:
                all_list.remove(all_list[x])
    return all_list


def assess_image(new_list):
    """Display image and prompt for assessment of cloud impacts, update the dict"""
    for file in new_list:
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

        dict_entry = {timestamp: {'farm_visible': farm_visible,
                                  'vis_moisture': vis_moisture,
                                  'e18': e18,
                                  'hay_field': hay_field,
                                  'cedar_hill': cedar_hill}}

        for k, v in dict_entry[timestamp].items():
            if v.lower() == 'y':
                dict_entry[timestamp][k] = True
            elif v.lower() == 'n':
                dict_entry[timestamp][k] = False

        pic_dict.update(dict_entry)


def update_cloud_data(data_dict):
    """Open file for writing and replace contents with updated dictionary data"""
    file_content = json.dumps(data_dict)
    with open('../stats/votm/cloud.json', 'w') as outfile:
        outfile.write(file_content)


if __name__ == '__main__':
    pic_dict = get_current_data()
    curr_list = list(pic_dict.keys())
    update_list = filter_file_list(curr_list)
    assess_image(update_list)
    update_cloud_data(pic_dict)
