from src.general import *
from src.lineup import Lineup
import json
from sys import exit
import argparse
import itertools
from math import factorial


def do_generate(args: argparse.Namespace):
    print("Generating")
    lineup = Lineup.get_lineup()
    lineup.make_best()
    with open(output_dir("lineup.json"), "w") as lineup_file:
        lineup_dict = lineup.to_dict()
        json.dump(lineup_dict, lineup_file, indent=4)
        # print(json.dumps(lineup_dict, indent=4))
    lineup.to_csv(output_dir("lineup.csv"))
    print(lineup.get_overall())


def do_team_for_price(args: argparse.Namespace):
    val = int(vars(args).get("val", 0))
    print(f"Team for {val}")
    with open(output_dir("lineup.json"), "r") as lineup_file:
        lineup_dict: dict[str, dict] = json.load(lineup_file)
        all_positions = lineup_dict.get("players", {})
        all_players = list(
            player for position in all_positions.values() for player in position if player.get('ovr') > 84
        )
        num_players = len(all_players)
        num_players_factorial = factorial(num_players)
        print('; '.join(player.get('name') for player in all_players))
        filtered_combos = []
        for i in range(min(5, len(all_players)), 1, -1):
            print(f"Combinations of length {i}")
            all_combos = itertools.combinations(all_players, i)
            num_combos = int(num_players_factorial / (factorial(num_players - i) * factorial(i)))
            for (n, combo) in enumerate(all_combos):
                print(f"Checking combination {n} out of {num_combos}")
                total_price = sum(player.get("price", 0) for player in combo)
                if total_price < val and not any(
                    set(player.get('id') for player in combo).issuperset(set(player.get('id') for player in curr_combo)) for curr_combo in filtered_combos
                ):
                    filtered_combos.append(sorted(combo, key=lambda p: p.get("name")))
        for combo in filtered_combos:
            print("; ".join(player.get("name", "") for player in combo))


parser: argparse.ArgumentParser = argparse.ArgumentParser(
    prog="MutTeamGen", description="Generates a MUT team from mut.gg"
)
subparsers: argparse._SubParsersAction = parser.add_subparsers()

generate_subparser: argparse.ArgumentParser = subparsers.add_parser(
    "generate", help="Generate a lineup based on provided team options"
)
generate_subparser.add_argument("--teams", action="append")
generate_subparser.set_defaults(func=do_generate)

for_price_subparser: argparse.ArgumentParser = subparsers.add_parser(
    "team-for-price",
    help="From a generated lineup, see what options you have given a number of coins",
)
for_price_subparser.add_argument("val", action="store")
for_price_subparser.set_defaults(func=do_team_for_price)

args = parser.parse_args()
args.func(args)
