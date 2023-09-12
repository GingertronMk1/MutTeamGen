import requests
from bs4 import BeautifulSoup

def get_api_player(id):
  return requests.get(f"https://www.mut.gg/api/mutdb/player-items/{id}").json()

def get_api_player_from_web_link(link):
  split_link = link.split('/')
  id = split_link[-1]
  return get_api_player(id)

vgm_url = 'https://www.mut.gg/players'
html_text = requests.get(vgm_url).text
soup = BeautifulSoup(html_text, 'html.parser')

for link in soup.find_all('a', class_='player-list-item__link'):
  player = get_api_player_from_web_link(link.get('href'))
  first = player.get('firstName')
  last = player.get('lastName')
  print(f"{first} {last}")

