import copy
from dataclasses import dataclass
import json
import requests
from sys import exit
from bs4 import BeautifulSoup

FROM_INTERNET = True

position_numbers = {
    "QB": 2,
    "HB": 3,
    "FB": 1,
    "WR": 5,
    "TE": 3,
    "LT": 2,
    "LG": 2,
    "C": 2,
    "RG": 2,
    "RT": 2,
    "LE": 2,
    "RE": 2,
    "DT": 4,
    "LOLB": 2,
    "MLB": 4,
    "ROLB": 2,
    "CB": 5,
    "FS": 2,
    "SS": 2,
    "K": 1,
    "P": 1,
}


def gen_lineup():
    global position_numbers
    lineup = {}
    for key in position_numbers.keys():
        lineup[key] = list()
    return lineup


def get_api_player(id):
    try:
        return (
            requests.get(f"https://www.mut.gg/api/mutdb/player-items/{id}")
            .json()
            .get("data")
        )
    except:
        return None


def get_api_player_from_web_link(link):
    split_link = list(s for s in link.split("/") if s)
    player_id = split_link[-1]
    return get_api_player(player_id)


def get_lineup_for_team(team):
    lineup = gen_lineup()
    base_url = "https://www.mut.gg/players"
    for page in range(1, 300):
        retrieved_page = requests.get(
            base_url, params={"page": page, "team_chem": team}
        )
        print(retrieved_page.url)
        if retrieved_page.status_code != 200:
            return lineup
        retrieved_page = BeautifulSoup(retrieved_page.text, "html.parser")
        for lkey, link in enumerate(
            retrieved_page.find_all("a", class_="player-list-item__link")
        ):
            print(f"{page} | {lkey}")
            href = link.get("href")
            retrieved_player = get_api_player_from_web_link(href)
            if retrieved_player is not None:
                position = retrieved_player.get("position").get("abbreviation")
                firstName = retrieved_player.get("firstName")
                lastName = retrieved_player.get("lastName")
                add_condition = all(
                    [
                        len(lineup[position]) < position_numbers[position],
                        not any(
                            curr.get("firstName") == firstName
                            and curr.get("lastName") == lastName
                            for curr in lineup[position]
                        ),
                    ]
                )
                if add_condition:
                    lineup[position].append(copy.deepcopy(retrieved_player))
                    print(f"Added {firstName} {lastName}")
                fulls = list()
                for position, number in position_numbers.items():
                    print(f"{position}: {len(lineup[position])}/{number}")
                    fulls.append(len(lineup[position]) >= number)
                if all(fulls):
                    print("All Full Up")
                    return lineup
    print("Exhausted")
    return lineup


def get_lineup():
    original_lineup = gen_lineup()
    acceptable_teams = ["sea", "phi"]
    for team in acceptable_teams:
        original_lineup = merge_lineups(original_lineup, get_lineup_for_team(team))
    return original_lineup


def merge_lineups(lineup_1, lineup_2):
    global position_numbers
    new_lineup = gen_lineup()
    for position, players in lineup_1.items():
        lineup_2_players_in_position = lineup_2.get(position, [])
        number_of_players_at_position = position_numbers.get(position, 0)
        print(number_of_players_at_position)
        new_players = sorted(
            players + lineup_2_players_in_position,
            key=lambda player: player.get("overall", 0),
            reverse=True,
        )[0:number_of_players_at_position]
        for player in new_players:
            new_lineup[position].append(player)
    return new_lineup


lineup = get_lineup()

with open("lineup.json", "w") as lineup_file:
    json.dump(lineup, lineup_file, indent=4)

for pos, players in lineup.items():
    pos_players = ", ".join(
        f"{player.get('overall')} {player.get('firstName')} {player.get('lastName')}"
        for player in players
    )
    print(f"{pos}: {pos_players}")
