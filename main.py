from src.general import *
from src.lineup import Lineup
import json


lineup = Lineup.get_lineup()

lineup.make_best()

with open(output_dir("lineup.json"), "w") as lineup_file:
    lineup_dict = lineup.to_dict()
    json.dump(lineup_dict, lineup_file, indent=4)
    print(json.dumps(lineup_dict, indent=4))

lineup.to_csv(output_dir("lineup.csv"))

print(lineup.get_overall())
