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


def argparser() -> argparse.ArgumentParser:
    parser: argparse.ArgumentParser = argparse.ArgumentParser(
        prog="MutTeamGen", description="Generates a MUT team from mut.gg"
    )
    subparsers: argparse._SubParsersAction = parser.add_subparsers()

    generate_subparser: argparse.ArgumentParser = subparsers.add_parser(
        "generate", help="Generate a lineup based on provided team options"
    )
    generate_subparser.add_argument("--teams", action="append")

    for_price_subparser: argparse.ArgumentParser = subparsers.add_parser(
        "team-for-price",
        help="From a generated lineup, see what options you have given a number of coins",
    )
    for_price_subparser.add_argument("val", action="store")
    return parser


def args() -> argparse.Namespace:
    return argparser().parse_args()
