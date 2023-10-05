from dataclasses import dataclass
from bs4 import BeautifulSoup
import requests
from typing import Optional


@dataclass
class Player:
    PRICE_KEY = "xbsxPrice"
    id: str
    name: str
    ovr: int
    pos: str
    program: str
    price: int | None
    chem: str

    @staticmethod
    def from_dict(input: dict, chem: str | None = None) -> "Player":
        fullName = f"{input.get('firstName')} {input.get('lastName')}"
        if not chem:
            team = input.get("team")
            if team is None:
                raise ValueError("No Team")
            chem = team.get("abbreviation", "").lower()
        if chem is None:
            chem = ""
        return Player(
            str(input.get("externalId", 0)),
            fullName,
            input.get("maxOverall", 0),
            input.get("position", {}).get("abbreviation", "").lower(),
            input.get("program", {}).get("name", ""),
            input.get(Player.PRICE_KEY),
            chem,
        )

    def __str__(self) -> str:
        return f"{self.ovr}OVR {self.program} {self.name} ({self.chem.upper()}) / {self.get_price()}"

    def get_price(self) -> str:
        if self.price is None:
            return "NAT"
        formatted_price = "{:,}".format(self.price)
        return f"{formatted_price} coins"

    def get_player_id(self) -> str:
        return self.id[-5:]

    @staticmethod
    def get_api_player(id: str, team: str) -> Optional["Player"]:
        try:
            ret_val: dict = (
                requests.get(f"https://www.mut.gg/api/mutdb/player-items/{id}")
                .json()
                .get("data")
            )
            if ret_val.get("program", {}).get("id", 0) != 240:
                return Player.from_dict(ret_val, team)
        except:
            pass
        return None

    @staticmethod
    def get_api_player_from_web_link(link: str, team: str) -> Optional["Player"]:
        split_link = list(s for s in link.split("/") if s)
        player_id = split_link[-1]
        return Player.get_api_player(player_id, team)

    @staticmethod
    def get_api_players_from_web_page(page_number: int, team: str) -> list["Player"]:
        base_url = "https://www.mut.gg/players"
        params: dict[str, int | str] = {"page": page_number, "team_chem": team, "max_ovr": "on"}
        retrieved_page = requests.get(base_url, params=params)
        if retrieved_page.status_code != 200:
            return []
        retrieved_text: str = retrieved_page.text
        retrieved_page_soup = BeautifulSoup(retrieved_text, "html.parser")
        ret_val = list()
        for lkey, link in enumerate(
            retrieved_page_soup.find_all("a", class_="player-list-item__link")
        ):
            print(f"{team.upper()} {page_number} | {lkey}")
            href = link.get("href")
            retrieved_player = Player.get_api_player_from_web_link(href, team)
            if retrieved_player is not None:
                ret_val.append(retrieved_player)
        return ret_val
