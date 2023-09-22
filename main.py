import copy
import csv
from dataclasses import dataclass, field
import json
import requests
from bs4 import BeautifulSoup

FROM_INTERNET = True

@dataclass
class Position:
    name: str
    abbreviation: str
    max_in_lineup: int
    num_in_ovr: int
@dataclass
class Player:
    id: str
    name: str
    ovr: int
    pos: str
    program: str
    chem: str

    @staticmethod
    def from_dict(input: dict, chem: str|None = None) -> "Player":
        fullName = f"{input.get('firstName')} {input.get('lastName')}"
        if chem is None:
            team = input.get('team')
            if team is None:
                raise ValueError("No Team")
            chem = team.get('abbreviation').lower()
        return Player(
            str(input.get('externalId', 0)),
            fullName,
            input.get('maxOverall', 0),
            input.get('position', {}).get('abbreviation', '').lower(),
            input.get('program', {}).get('name', ''),
            chem
        )
    
    def __str__(self) -> str:
        return f"{self.ovr}OVR {self.program} {self.name} ({self.chem.upper()})"

    def get_player_id(self) -> str:
        return self.id[-5:]


@dataclass
class Lineup:
    qb: list[Player] = field(default_factory=list)
    hb: list[Player] = field(default_factory=list)
    fb: list[Player] = field(default_factory=list)
    wr: list[Player] = field(default_factory=list)
    te: list[Player] = field(default_factory=list)
    lt: list[Player] = field(default_factory=list)
    lg: list[Player] = field(default_factory=list)
    c: list[Player] = field(default_factory=list)
    rg: list[Player] = field(default_factory=list)
    rt: list[Player] = field(default_factory=list)
    le: list[Player] = field(default_factory=list)
    re: list[Player] = field(default_factory=list)
    dt: list[Player] = field(default_factory=list)
    lolb: list[Player] = field(default_factory=list)
    mlb: list[Player] = field(default_factory=list)
    rolb: list[Player] = field(default_factory=list)
    cb: list[Player] = field(default_factory=list)
    fs: list[Player] = field(default_factory=list)
    ss: list[Player] = field(default_factory=list)
    k: list[Player] = field(default_factory=list)
    p: list[Player] = field(default_factory=list)

    @staticmethod
    def get_positions() -> dict[str, Position]:
      return {
          "qb": Position("Quarterback", "qb", 2, 1),
          "hb": Position("Halfback", "hb", 3, 2),
          "fb": Position("Fullback", "fb", 1, 1),
          "wr": Position("Wide Receiver", "wr", 5, 3),
          "te": Position("Tight End", "te", 3, 2),
          "lt": Position("Left Tackle", "lt", 2, 1),
          "lg": Position("Left Guard", "lg", 2, 1),
          "c": Position("Center", "c", 2, 1),
          "rg": Position("Right Guard", "rg", 2, 1),
          "rt": Position("Right Tackle", "rt", 2, 1),
          "le": Position("Left End", "le", 2, 1),
          "re": Position("Right End", "re", 2, 1),
          "dt": Position("Defensive Tackle", "dt", 4, 2),
          "lolb": Position("Left Outside Linebacker", "lolb", 2, 1),
          "mlb": Position("Middle Linebacker", "mlb", 4, 2),
          "rolb": Position("Right Outside Linebacker", "rolb", 2, 1),
          "cb": Position("Cornerback", "cb", 5, 3),
          "fs": Position("Free Safety", "fs", 2, 1),
          "ss": Position("Strong Safety", "ss", 2, 1),
          "k": Position("Kicker", "k", 1, 1),
          "p": Position("Punter", "p", 1, 1),
      }

    def get_overall(self) -> int:
        ovr_sum: int = 0
        ovr_num: int = 0
        for (abbrev, position) in Lineup.get_positions().items():
            for player in getattr(self, abbrev)[0:position.num_in_ovr]:
                ovr_sum += player.ovr
                ovr_num += 1
        return int(round(ovr_sum / ovr_num))

    def is_full(self) -> bool:
        for (position, number) in self.get_positions().items():
            if len(getattr(self, position)) < number.max_in_lineup:
                return False
        return True

    def get_chem_numbers(self) -> dict[str, int]:
        ret_val: dict[str, int] = {}
        for position in self.get_positions().keys():
            for player in getattr(self, position):
                ret_val[player.chem] = ret_val.get(player.chem, 0) + 1
        return ret_val


    def to_dict(self) -> dict:
        players = {}
        for (position, pos_players) in self.players_as_dict().items():
            players[position] = [str(player) for player in pos_players]
        return {
            'totals': self.get_chem_numbers(),
            'players': players
        }

    def players_as_dict(self) -> dict[str, list['Player']]:
        players = {}
        for position in self.get_positions().keys():
            players_in_position = getattr(self, position)
            players[position] = players_in_position
        return players

    def to_csv(self, out_file_name = 'lineup.csv') -> None:
        with open(out_file_name, 'w') as out_file:
            to_write: list[list] = []
            to_write.append(['Position', 'Name', 'OVR', 'Chem', 'Program'])
            for (position, players) in self.players_as_dict().items():
                for player in players:
                    to_write.append([position.upper(), player.name, player.ovr, player.chem.upper(), player.program])
                to_write.append([None])
            chems = []
            numbers = []
            for (chem, number) in self.get_chem_numbers().items():
                chems.append(chem.upper())
                numbers.append(number)
            to_write.extend([chems, numbers, []])
            to_write.append(['OVR', lineup.get_overall()])
            writer = csv.writer(out_file)
            writer.writerows(square_off_list_of_lists(to_write))

def square_off_list_of_lists(input: list[list]) -> list[list]:
    target_length = max(len(l) for l in input)
    return list(pad_list(l, target_length) for l in input)

def pad_list(input_list: list, target_length: int) -> list:
    return input_list + [None] * (target_length - len(input_list))

def gen_lineup():
    lineup = {}
    for key in Lineup.get_positions().keys():
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
            api_player = get_api_player_from_web_link(href)
            if api_player.get('program', {}).get('id', 0) != 240:
              retrieved_player = Player.from_dict(api_player, team)
              if retrieved_player is not None:
                  position = retrieved_player.pos
                  position_players = getattr(lineup, position)
                  add_condition = retrieved_player.get_player_id() not in list(pos_player.get_player_id() for pos_player in position_players)
                  if add_condition:
                      position_players.append(copy.deepcopy(retrieved_player))
                      setattr(lineup, position, position_players)
                      print(f"Added {retrieved_player.name}")
                  for position, number in Lineup.get_positions().items():
                      position_players = getattr(lineup, position)
                      # print(f"{position}: {len(position_players)}/{number.max_in_lineup}")
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

def get_player_id(player: dict[str, str]) -> str:
    return str(player.get("externalId", 0))[-5:]


def merge_lineups(lineup_1: Lineup, lineup_2: Lineup):
    new_lineup = Lineup()
    for (position, number) in Lineup.get_positions().items():
        joined_lineup = getattr(lineup_1, position)
        for player in getattr(lineup_2, position):
            if player.get_player_id() not in list(lineup_1_player.get_player_id() for lineup_1_player in joined_lineup):
                joined_lineup.append(player)
        new_players = sorted(
            joined_lineup,
            key=lambda player: player.ovr,
            reverse= True
        )[0:number.max_in_lineup]
        setattr(new_lineup, position, new_players)
    return new_lineup

def output_dir(subdir: str) -> str:
    return f"./output/{subdir}"

lineup = get_lineup()

with open(output_dir('lineup.json'), "w") as lineup_file:
    lineup_dict = lineup.to_dict()
    json.dump(lineup_dict, lineup_file, indent=4)
    print(json.dumps(lineup_dict, indent=4))

lineup.to_csv(output_dir('lineup.csv'))

print(lineup.get_overall())