from dataclasses import dataclass
import json
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
    price: int
    chem: str
    ratings: dict[str, int]

    @staticmethod
    def from_dict(
        input: dict, chem: str | None = None, ratings: dict[str, int] | None = None
    ) -> "Player":
        fullName = f"{input.get('firstName')} {input.get('lastName')}"
        if not chem:
            team = input.get("team")
            if team is None:
                raise ValueError("No Team")
            chem = team.get("abbreviation", "").lower()
        if chem is None:
            chem = ""
        price = input.get(Player.PRICE_KEY, 0)
        if price is None:
            price = 0
        price = int(price)
        if ratings is None:
            ratings = {}
        return Player(
            str(input.get("externalId", 0)),
            fullName,
            input.get("maxOverall", 0),
            input.get("position", {}).get("abbreviation", "").lower(),
            input.get("program", {}).get("name", ""),
            price,
            chem,
            ratings,
        )

    def __str__(self) -> str:
        return f"{self.ovr}OVR {self.program} {self.name} ({self.chem.upper()}) / {self.get_price()}"

    def get_price(self) -> str:
        if self.price == 0:
            return "NAT"
        formatted_price = "{:,}".format(self.price)
        return f"{formatted_price} coins"

    def get_player_id(self) -> str:
        return self.id[-5:]

    @staticmethod
    def get_api_player(id: str, team: str) -> Optional["Player"]:
        ret_val = None
        try:
            ret_val: dict = (
                requests.get(f"https://www.mut.gg/api/mutdb/player-items/{id}")
                .json()
                .get("data")
            )
        except:
            pass
        if ret_val is not None:
            return Player.from_dict(ret_val, team)
        return None

    @staticmethod
    def get_ratings_from_web_link(link: str) -> dict[str, int]:
        ratings = {}
        base_url = "https://www.mut.gg"
        player_url = f"{base_url}{link}"
        request_response = requests.get(player_url)
        print(f"{player_url} returns {request_response.status_code}")
        soup = BeautifulSoup(request_response.content, "html.parser")
        for rating in soup.find_all(class_="rating"):
            rating_name = rating.find(class_="rating__label").text
            rating_value = rating.find(class_="rating__value").text
            ratings[rating_name] = rating_value
        return ratings

    @staticmethod
    def get_api_player_from_web_link(link: str, team: str) -> Optional["Player"]:
        split_link = list(s for s in link.split("/") if s and not s.startswith("?"))
        player_id = split_link[-1]
        player_ratings = Player.get_ratings_from_web_link(link)
        player = Player.get_api_player(player_id, team)
        if player is not None:
            player.ratings = player_ratings
        return player

    @staticmethod
    def get_api_players_from_web_page(page_number: int, team: str) -> list["Player"]:
        base_url = "https://www.mut.gg/players"
        params: dict[str, int | str] = {
            "page": page_number,
            "team_chem": team,
            "max_ovr": "on",
        }
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
