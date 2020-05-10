import json
import os
from pprint import pprint as pp


def print_from_file(date_list):
    for fn in os.listdir('./stats/brass/'):
        if fn.split('_')[0] in date_list and fn.endswith('cloud.json'):
            with open(f'./stats/brass/{fn}') as in_file:
                cloud_dict = json.load(in_file)
            with open('./stats/cloud_comparison.txt', 'a') as outfile:
                outfile.write(f"{cloud_dict['max']:^10}"
                              f"{cloud_dict['num_cld_pixels']:^10}"
                              f"{cloud_dict['pixels']:^10}"
                              f"{cloud_dict['median']:^10}"
                              f"{cloud_dict['25_percentile']:^10}"
                              f"{cloud_dict['75_percentile']:^10}\n")

def write_divider(divider_label):
    with open('./stats/cloud_comparison.txt', 'a') as outfile:
        outfile.write(f"{divider_label:-^50}\n")

if __name__ == '__main__':
    with open('./stats/cloud_comparison.txt', 'w') as format_data:
        format_data.write(f"{'Max':^10}{'Num Cld Px':^10}{'Pixels':^10}{'Median':^10}{'25%':^10}{'75%':^10}\n")
    write_divider('Clear')
    print_from_file(['20200428', '20200430'])
    write_divider('Cloudy')
    print_from_file(['20200420', '20200503'])
    write_divider('Overcast')
    print_from_file(['20200425', '20200428'])
