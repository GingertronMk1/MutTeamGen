from dataclasses import dataclass, field
from src.player import Player
from src.position import Position
import csv
from datetime import datetime
import json
import multiprocessing
from src.general import *


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
            "fb": Position("Fullback", "fb", 2, 1),
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
        for abbrev, position in Lineup.get_positions().items():
            for player in getattr(self, abbrev)[0 : position.num_in_ovr]:
                ovr_sum += player.ovr
                ovr_num += 1
        return int(round(ovr_sum / ovr_num))

    def is_full(self) -> bool:
        for position, number in self.get_positions().items():
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
        for position, pos_players in self.players_as_dict().items():
            players[position] = [str(player) for player in pos_players]
        return {"totals": self.get_chem_numbers(), "players": players}

    def players_as_dict(self) -> dict[str, list["Player"]]:
        players = {}
        for position in self.get_positions().keys():
            players_in_position = getattr(self, position)
            players[position] = players_in_position
        return players

    def total_price_formatted(self) -> str:
        return "{:,}".format(self.total_price())

    def total_price(self) -> int:
        total: int = 0
        for position in self.get_positions().keys():
            total = total + sum(player.price or 0 for player in getattr(self, position))
        return total

    def to_csv(self, out_file_name: str = "lineup.csv") -> None:
        with open(out_file_name, "w") as out_file:
            to_write: list[list] = []
            now = datetime.now()
            to_write.append(
                [
                    "Position",
                    "Name",
                    "OVR",
                    "Chem",
                    "Program",
                    f"Price at {now.strftime('%Y-%m-%d %H:%M')}",
                ]
            )
            for position, players in self.players_as_dict().items():
                for player in players:
                    to_write.append(
                        [
                            position.upper(),
                            player.name,
                            player.ovr,
                            player.chem.upper(),
                            player.program,
                            player.get_price(),
                        ]
                    )
                to_write.append([None])
            to_write.append(
                [
                    "TOTAL PRICE",
                    None,
                    None,
                    None,
                    None,
                    f"{self.total_price_formatted()} coins",
                ]
            )
            to_write.append([None])
            chems = []
            numbers = []
            for chem, number in self.get_chem_numbers().items():
                chems.append(chem.upper())
                numbers.append(number)
            to_write.extend([chems, numbers, []])
            to_write.append(["OVR", self.get_overall()])
            writer = csv.writer(out_file)
            writer.writerows(square_off_list_of_lists(to_write))

    def make_best(self) -> None:
        for abbrev, position in self.get_positions().items():
            position_players: list[Player] = getattr(self, abbrev)
            position_players.sort(key=lambda p: p.price)
            position_players.sort(key=lambda p: p.ovr, reverse=True)
            new_players: list[Player] = list()
            for player in position_players:
                if player.get_player_id() not in list(
                    new_player.get_player_id() for new_player in new_players
                ):
                    new_players.append(player)
            setattr(self, abbrev, new_players[0 : position.max_in_lineup])

    @staticmethod
    def get_lineup() -> "Lineup":
        with open("acceptable_teams.json") as jsonTeams:
            acceptable_teams: list[str] = json.load(jsonTeams)
        if all(team for team in acceptable_teams):
            print(", ".join(acceptable_teams))
        else:
            print("All teams viewed")
        original_lineup = Lineup()
        combinations: list[tuple[int, str]] = list(
            (page, team_chem)
            for page in range(1, 100)
            for team_chem in acceptable_teams
        )
        with multiprocessing.Pool() as pool:
            for players in pool.starmap(
                Player.get_api_players_from_web_page, combinations
            ):
                for player in players:
                    position = player.pos
                    current_pos_players = getattr(original_lineup, position)
                    current_pos_players.append(player)
                    setattr(original_lineup, position, current_pos_players)
        return original_lineup
