import copy
from dataclasses import dataclass, field
import json
import requests
from bs4 import BeautifulSoup

FROM_INTERNET = True


@dataclass
class Lineup:
    qb: list = field(default_factory=list)
    hb: list = field(default_factory=list)
    fb: list = field(default_factory=list)
    wr: list = field(default_factory=list)
    te: list = field(default_factory=list)
    lt: list = field(default_factory=list)
    lg: list = field(default_factory=list)
    c: list = field(default_factory=list)
    rg: list = field(default_factory=list)
    rt: list = field(default_factory=list)
    le: list = field(default_factory=list)
    re: list = field(default_factory=list)
    dt: list = field(default_factory=list)
    lolb: list = field(default_factory=list)
    mlb: list = field(default_factory=list)
    rolb: list = field(default_factory=list)
    cb: list = field(default_factory=list)
    fs: list = field(default_factory=list)
    ss: list = field(default_factory=list)
    k: list = field(default_factory=list)
    p: list = field(default_factory=list)

    @staticmethod
    def get_position_numbers() -> dict[str, int]:
      return {
          "qb": 2,
          "hb": 3,
          "fb": 1,
          "wr": 5,
          "te": 3,
          "lt": 2,
          "lg": 2,
          "c": 2,
          "rg": 2,
          "rt": 2,
          "le": 2,
          "re": 2,
          "dt": 4,
          "lolb": 2,
          "mlb": 4,
          "rolb": 2,
          "cb": 5,
          "fs": 2,
          "ss": 2,
          "k": 1,
          "p": 1,
      }

    def is_full(self) -> bool:
        for (position, number) in self.get_position_numbers().items():
            if len(getattr(self, position)) < number:
                return False
        return True

    def to_dict(self) -> dict[str, list[str]]:
        ret_val = {}
        for position in self.get_position_numbers().keys():
            ret_val[position] = [f"{player.get('overall')}OVR {player.get('firstName')} {player.get('lastName')}" for player in getattr(self, position)]
        return ret_val


def gen_lineup():
    lineup = {}
    for key in Lineup.get_position_numbers().keys():
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
    lineup = Lineup()
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
                position = retrieved_player.get("position").get("abbreviation").lower()
                firstName = retrieved_player.get("firstName")
                lastName = retrieved_player.get("lastName")
                position_players = getattr(lineup, position)
                add_condition = all(
                    [
                        len(position_players) < Lineup.get_position_numbers()[position],
                        not any(
                            curr.get("firstName") == firstName
                            and curr.get("lastName") == lastName
                            for curr in position_players
                        ),
                    ]
                )
                if add_condition:
                    position_players.append(copy.deepcopy(retrieved_player))
                    setattr(lineup, position, position_players)
                    print(f"Added {firstName} {lastName}")
                for position, number in Lineup.get_position_numbers().items():
                    position_players = getattr(lineup, position)
                    print(f"{position}: {len(position_players)}/{number}")
                if lineup.is_full():
                    print("All Full Up")
                    return lineup
    print("Exhausted")
    return lineup


def get_lineup():
    original_lineup = Lineup()
    acceptable_teams = ["sea", "phi"]
    for team in acceptable_teams:
        original_lineup = merge_lineups(original_lineup, get_lineup_for_team(team))
    return original_lineup


def merge_lineups(lineup_1: Lineup, lineup_2: Lineup):
    new_lineup = Lineup()
    for (position, number) in Lineup.get_position_numbers().items():
        joined_lineup = getattr(lineup_1, position)
        for player in getattr(lineup_2, position):
            if player.get("externalId") not in list(lineup_1_player.get("id") for lineup_1_player in joined_lineup):
                joined_lineup.append(player)
        new_players = sorted(
            joined_lineup,
            key=lambda player: player.get("overall", 0),
            reverse= True
        )[0:number]
        setattr(new_lineup, position, new_players)
    return new_lineup


lineup = get_lineup()

with open("lineup.json", "w") as lineup_file:
    json.dump(lineup.to_dict(), lineup_file, indent=4)

for (pos, players) in lineup.to_dict().items():
    pos_players = ", ".join(players)
    print(f"{pos}: {pos_players}")
