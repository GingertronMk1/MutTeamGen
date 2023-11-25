from dataclasses import dataclass, field
from src.player import Player
from src.position import Position
import csv
from datetime import datetime
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

    def get_overall(self) -> int:
        ovr_sum: int = 0
        ovr_num: int = 0
        for position in Position.get_all():
            for player in getattr(self, position.abbreviation)[0 : position.num_in_ovr]:
                ovr_sum += player.ovr
                ovr_num += 1
        return int(round(ovr_sum / ovr_num))

    def is_full(self) -> bool:
        for position in Position.get_all():
            if len(getattr(self, position.abbreviation)) < position.max_in_lineup:
                return False
        return True

    def get_chem_numbers(self) -> dict[str, int]:
        ret_val: dict[str, int] = {}
        for position in [pos.abbreviation for pos in Position.get_all()]:
            for player in getattr(self, position):
                ret_val[player.chem] = ret_val.get(player.chem, 0) + 1
        return sort_dict(ret_val, by_key=False)

    def to_dict(self) -> dict:
        players = {}
        for position, pos_players in self.players_as_dict().items():
            players[position] = [player.__dict__ for player in pos_players]
        return {"totals": self.get_chem_numbers(), "players": players}

    def players_as_dict(self) -> dict[str, list["Player"]]:
        players = {}
        for position in [pos.abbreviation for pos in Position.get_all()]:
            players_in_position = getattr(self, position)
            players[position] = players_in_position
        return players

    def total_price_formatted(self) -> str:
        return "{:,}".format(self.total_price())

    def total_price(self) -> int:
        total: int = 0
        for position in [pos.abbreviation for pos in Position.get_all()]:
            total = total + sum(player.price or 0 for player in getattr(self, position))
        return total

    def to_markdown(self, out_file_name: str = "lineup.md") -> None:
        with open(out_file_name, "w") as out_file:
            to_write: list[list] = []
            now = datetime.now()
            header_row = [
                "Position",
                "Name",
                "OVR",
                "Chem",
                "Program",
                f"Price at {now.strftime('%Y-%m-%d %H:%M')}",
            ]
            to_write.append(header_row)
            to_write.append(["---"] * len(header_row))
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
            lineup_str = "\n".join(
                " | ".join(str(item) for item in row) for row in to_write
            )
            chems_list: list[list] = [["Chem", "Number"], ["---", "---"]]
            for chem, number in self.get_chem_numbers().items():
                chems_list.append([chem.upper(), number])
            chems_str = "\n".join(
                " | ".join(str(item) for item in row) for row in chems_list
            )
            out_file.write("\n\n".join([lineup_str, chems_str]))

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
        for position in Position.get_all():
            position_players: list[Player] = getattr(self, position.abbreviation)
            position_players.sort(key=lambda p: (p.ovr, 0 - p.price), reverse=True)
            new_players: list[Player] = list()
            for player in position_players:
                if player.get_player_id() not in list(
                    new_player.get_player_id() for new_player in new_players
                ):
                    new_players.append(player)
            setattr(
                self, position.abbreviation, new_players[0 : position.max_in_lineup]
            )

    @staticmethod
    def get_lineup(acceptable_teams: list[str]) -> "Lineup":
        if len(acceptable_teams) > 0:
            print(", ".join(acceptable_teams))
        else:
            print("All teams viewed")
            acceptable_teams = [""]
        original_lineup = Lineup()
        combinations: list[tuple[str, Position]] = list(
            (team_chem, position)
            for team_chem in acceptable_teams
            for position in Position.get_all()
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
