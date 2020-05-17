# TODO: import required packages
import simplekml
import os
from datetime import datetime as dt
import requests
from pprint import pprint as pp
import zipfile
import json
import shutil

votm_bounds = {
    'north': 42.181135,
    'south': 42.158807,
    'east': -89.130023,
    'west': -89.160000
}

brass_bounds = {
    'north': 42.160869,
    'south': 42.143881,
    'east': -89.171437,
    'west': -89.193792
}


# add new icon to kml file
# TODO: include ability to generate kmls for votm as well (need new lat/lon box)
def add_groundoverlay(str_date, veg_index, stats_dict, fn, farm):
    '''This function adds a new overlay section to the kml file'''
    ground = kml.newgroundoverlay(name=str_date,
                                  description=f'{veg_index.upper()} stats:\nMean - {stats_dict["Farm boundary"]["mean"]:.3f}\nMedian - {stats_dict["Farm boundary"]["median"]:.3f}\nMin - {stats_dict["Farm boundary"]["min"]:.3f}\nMax - {stats_dict["Farm boundary"]["max"]:.3f}')
    ground.icon.href = f"files/{fn}"
    ground.icon.viewboundscale = 0.75
    if farm == 'votm':
        bound_dict = votm_bounds
    elif farm == 'brass':
        bound_dict = brass_bounds

    ground.latlonbox.north = bound_dict['north']
    ground.latlonbox.south = bound_dict['south']
    ground.latlonbox.east = bound_dict['east']
    ground.latlonbox.west = bound_dict['west']


# build folder
def build_dir():
    '''Creates the kmz_dir and subdirectory files in the current working dir'''
    os.mkdir('../KMZs/kmz_dir/')
    os.mkdir('../KMZs/kmz_dir/files')

# tear down folder
def rm_dir():
    '''Removes (recursively) the kmz_dir'''
    os.rmdir('../KMZs/kmz_dir')

# zip folder as 'kmz'
def zip_kmz(farm, index, pic_list):
    '''Zips the file directory with the kml into a KMZ file'''
    zipf = zipfile.ZipFile(f'./KMZs/{farm.title()}_{index.upper()}.kmz', 'w', zipfile.ZIP_DEFLATED)
    zipf.write(f'../KMZs/{farm}_{index}.kml', arcname=f'./{farm}_{index}.kml')
    for g in pic_list:
        zipf.write(f'../pics/{farm}/{g}', arcname=f'./files/{g}')
    zipf.close()


# Clean up folder
def clean_folder():
    '''Removes the kml file as well as files directory'''
    if os.path.exists('groundoverlay.kml'):
        os.remove('groundoverlay.kml')
    filelist = [f for f in os.listdir('../KMZs/kmz_dir/files') if f.endswith('.png')]
    for g in filelist:
        os.remove(os.path.join('files', g))


def get_stats(farm, index, dt_data):
    '''Receives url and returns dictionary of stats for polygon'''
    with open(f'../stats/{farm}/{dt_data}_Farm boundary_{index}.json', 'r') as data_file:
        return json.load(data_file)

def get_farm():
    """Prompt user for a farm"""
    return input("Please enter either 'brass' or 'votm'\n").lower()

def get_index():
    """Prompt user for evi or NDVI"""
    return input("Please enter the desired index either evi or ndvi.\n").lower()


if __name__ == '__main__':
    farm = get_farm()
    veg_index = get_index()
    kml = simplekml.Kml()
    kml_pics = [x for x in os.listdir(f'../pics/{farm}/') if x[0:3] == f'{veg_index[0:3]}']
    kml_pics.sort()
    for fn in kml_pics:
        date_data = fn.split('_')[1][0:8]
        num_date = dt.strptime(date_data, "%Y%m%d")
        ltr_date = num_date.strftime("%b %-d, %Y")
        stats = get_stats(farm, veg_index, date_data)
        add_groundoverlay(ltr_date, veg_index, stats, fn, farm)
    kml.save(f'../KMZs/{farm}_{veg_index}.kml')
    zip_kmz(farm, veg_index, kml_pics)
    if os.path.exists(f'../KMZs/{farm.title()}_{veg_index.upper()}.kml'):
        os.remove(f'../KMZs/{farm.title()}_{veg_index.upper()}.kml')





