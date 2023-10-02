from dataclasses import dataclass


@dataclass
class Position:
    name: str
    abbreviation: str
    max_in_lineup: int
    num_in_ovr: int
