import json

with open('./stats/20200418_Farm boundary_evi.txt', 'r') as infile:
    clear_sky = json.load(infile)

with open('./stats/20200420_Farm boundary_evi.txt', 'r') as infile:
    few_clouds = json.load(infile)

with open('./stats/20200425_Farm boundary_evi.txt', 'r') as infile:
    total_clouds = json.load(infile)

with open('stats/evi_comparison.txt', 'w') as format_data:
    format_data.write(f"{'Name':>10}{'Clear':^15}{'Partly cloudy':^15}{'Overcast':^15}\n")

    for k, _ in clear_sky['Farm boundary'].items():
        format_data.write(f"{k:>10}"
              f"{clear_sky['Farm boundary'][k]:^15.3f}"
              f"{few_clouds['Farm boundary'][k]:^15.3f}"
              f"{total_clouds['Farm boundary'][k]:^15.3f}\n")