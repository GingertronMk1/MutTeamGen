from src.general import *
from src.lineup import Lineup
import json

print(argparser())

with open("acceptable_teams.json") as jsonTeams:
    acceptable_teams_list = json.load(jsonTeams)
    for acceptable_team_list in acceptable_teams_list:
        if len(acceptable_team_list) > 0:
            slugged_teams = "_".join(acceptable_team_list)
        else:
            slugged_teams = "all"
        print(slugged_teams)
        lineup = Lineup.get_lineup(acceptable_teams=acceptable_team_list)
        lineup.make_best()
        lineup.to_csv(output_dir(f"{slugged_teams}.csv"))
        lineup.to_markdown(output_dir(f"{slugged_teams}.md"))
