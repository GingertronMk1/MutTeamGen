import json
import requests
from bs4 import BeautifulSoup

def get_api_player(id):
  return requests.get(f"https://www.mut.gg/api/mutdb/player-items/{id}").json().get('data')

def get_api_player_from_web_link(link):
  split_link = list(s for s in link.split('/') if s)
  player_id = split_link[-1]
  print(player_id)
  return get_api_player(player_id)

vgm_url = 'https://www.mut.gg/players'
html_text = requests.get(vgm_url).text
soup = BeautifulSoup(html_text, 'html.parser')

for link in soup.find_all('a', class_='player-list-item__link'):
  href = link.get('href')
  print(href)
  player = get_api_player_from_web_link(href)
  firstName = player.get('firstName')
  lastName = player.get('lastName')
  # print(f"{firstName} {lastName}")
  print(json.dumps(player, indent=4))

