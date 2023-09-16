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
    "FB": 2,
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

lineup = {}

for key in position_numbers.keys():
  lineup[key] = list()

def get_api_player(id):
  try:
    return requests.get(f"https://www.mut.gg/api/mutdb/player-items/{id}").json().get('data')
  except:
    return None

def get_api_player_from_web_link(link):
  split_link = list(s for s in link.split('/') if s)
  player_id = split_link[-1]
  return get_api_player(player_id)

base_url = 'https://www.mut.gg/players'
html_text = requests.get(base_url).text
soup = BeautifulSoup(html_text, 'html.parser')

def get_lineup(lineup):
  acceptable_teams = [
      "sea","phi"
      ]
  players = list()
  for page in range(1,500):
    print(f"Checking {page}")
    for chem in acceptable_teams:
      retrieved_page = requests.get(f"{base_url}?page={page}&team_chem={chem}")
      if retrieved_page.status_code != 200:
        del retrieved_page
        print("Done!")
        continue
      retrieved_page = BeautifulSoup(retrieved_page.text, 'html.parser')
      for lkey, link in enumerate(retrieved_page.find_all('a', class_='player-list-item__link')):
        print(f"{page} | {lkey}")
        href = link.get('href')
        retrieved_player = get_api_player_from_web_link(href)
        if retrieved_player is not None:
          position = retrieved_player.get("position").get("abbreviation")
          firstName = retrieved_player.get('firstName')
          lastName = retrieved_player.get('lastName')
          add_condition = all([
                            len(lineup[position]) < position_numbers[position],
                            not any(curr.get('firstName') == firstName
                                    and curr.get('lastName') == lastName
                                    for curr in lineup[position]
                                ),
                            ])
          if add_condition:
            lineup[position].append(copy.deepcopy(retrieved_player))
            print(f"Added {firstName} {lastName}")
          fulls = list()
          for (position, number) in position_numbers.items():
            print(f"{position}: {len(lineup[position])}/{number}")
            fulls.append(len(lineup[position]) >= number)
          if all(fulls):
            return lineup
    return lineup

lineup = get_lineup(lineup)

with open("lineup.json", "w") as lineup_file:
  json.dump(lineup, lineup_file, indent=4)

for (pos, players) in lineup.items():
  pos_players = ', '.join(
    f"{player.get('overall')} {player.get('firstName')} {player.get('lastName')}"
    for player in players)
  print(f"{pos}: {pos_players}")
