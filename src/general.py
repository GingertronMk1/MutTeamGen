import requests
from bs4 import BeautifulSoup
import multiprocessing

def output_dir(subdir: str) -> str:
    return f"./output/{subdir}"


def square_off_list_of_lists(input: list[list]) -> list[list]:
    target_length = max(len(l) for l in input)
    return list(pad_list(l, target_length) for l in input)


def pad_list(input_list: list, target_length: int) -> list:
    return input_list + [None] * (target_length - len(input_list))




def get_player_id(player: dict[str, str]) -> str:
    return str(player.get("externalId", 0))[-5:]

