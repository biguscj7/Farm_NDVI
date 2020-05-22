import json
import os
from pprint import pprint as pp


def build_master_dict(index):
    index_dict = {'index': index}
    for fn in os.listdir('../project_files/stats/brass/'):
        if fn.endswith(f'{index_dict["index"]}.json'):
            with open(f'../stats/brass/{fn}', 'r') as infile:
                index_data = json.load(infile)
                index_date = fn.split('_')[0]
            index_dict.update({index_date: index_data})
    return index_dict

def average_dicts(date_list, index_dict):
    index_max, index_mean, index_median, index_std = 0, 0, 0, 0
    for k, v in index_dict.items():
        if k in date_list:
            index_max += v['Farm boundary']['max']
            index_mean += v['Farm boundary']['mean']
            index_median += v['Farm boundary']['median']
            index_std += v['Farm boundary']['std']
    return {'ave_max': index_max / 2,
            'ave_mean': index_mean / 2,
            'ave_median': index_median / 2,
            'ave_std': index_std / 2
            }

if __name__ == '__main__':
    index_dict = build_master_dict('evi')
    clear_dict = average_dicts(['20200418', '20200430'], index_dict)
    cloudy_dict = average_dicts(['20200420', '20200503'], index_dict)
    ovc_dict = average_dicts(['20200425', '20200428'], index_dict)

    with open('../project_files/stats/evi_comparison.txt', 'w') as format_data:
        format_data.write(f"{'Name':>10}{'Clear':^15}{'Partly cloudy':^15}{'Overcast':^15}\n")
        format_data.write(f"{'Max:':>10}{clear_dict['ave_max']:^15.3f}{cloudy_dict['ave_max']:^15.3f}{ovc_dict['ave_max']:^15.3f}\n")
        format_data.write(f"{'Mean:':>10}{clear_dict['ave_mean']:^15.3f}{cloudy_dict['ave_mean']:^15.3f}{ovc_dict['ave_mean']:^15.3f}\n")
        format_data.write(f"{'Median:':>10}{clear_dict['ave_median']:^15.3f}{cloudy_dict['ave_median']:^15.3f}{ovc_dict['ave_median']:^15.3f}\n")
        format_data.write(f"{'Std:':>10}{clear_dict['ave_std']:^15.3f}{cloudy_dict['ave_std']:^15.3f}{ovc_dict['ave_std']:^15.3f}\n")