import argparse

def output_dir(subdir: str) -> str:
    return f"./output/{subdir}"


def square_off_list_of_lists(input: list[list]) -> list[list]:
    target_length = max(len(l) for l in input)
    return list(pad_list(l, target_length) for l in input)


def pad_list(input_list: list, target_length: int) -> list:
    return input_list + [None] * (target_length - len(input_list))


def get_player_id(player: dict[str, str]) -> str:
    return str(player.get("externalId", 0))[-5:]


def sort_dict(d: dict, by_key: bool = True) -> dict:
    sort_key = 0 if by_key else 1
    sorted_vals = sorted(d.items(), key=lambda x: x[sort_key], reverse=not by_key)
    return dict(sorted_vals)

def argparser():
    parser: argparse.ArgumentParser = argparse.ArgumentParser(
                    prog='MutTeamGen',
                    description='Generates a MUT team from mut.gg')
    parser.add_argument('--include-captains',
                    action='store_true')  # on/off flag
    args = parser.parse_args()
    # print(args)
    return args