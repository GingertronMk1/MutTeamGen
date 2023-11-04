from dataclasses import dataclass


@dataclass
class Position:
    name: str
    abbreviation: str
    max_in_lineup: int
    num_in_ovr: int
    search_key_value: int

    @staticmethod
    def get_all() -> list["Position"]:
        return [
            Position("Quarterback", "qb", 2, 1, 1),
            Position("Halfback", "hb", 3, 2, 2),
            Position("Fullback", "fb", 2, 1, 3),
            Position("Wide Receiver", "wr", 5, 3, 4),
            Position("Tight End", "te", 3, 2, 5),
            Position("Left Tackle", "lt", 2, 1, 6),
            Position("Left Guard", "lg", 2, 1, 7),
            Position("Center", "c", 2, 1, 8),
            Position("Right Guard", "rg", 2, 1, 9),
            Position("Right Tackle", "rt", 2, 1, 10),
            Position("Left End", "le", 2, 1, 11),
            Position("Right End", "re", 2, 1, 12),
            Position("Defensive Tackle", "dt", 4, 2, 13),
            Position("Left Outside Linebacker", "lolb", 2, 1, 14),
            Position("Middle Linebacker", "mlb", 4, 2, 15),
            Position("Right Outside Linebacker", "rolb", 2, 1, 16),
            Position("Cornerback", "cb", 5, 3, 17),
            Position("Free Safety", "fs", 2, 1, 18),
            Position("Strong Safety", "ss", 2, 1, 19),
            Position("Kicker", "k", 1, 1, 20),
            Position("Punter", "p", 1, 1, 21),
        ]
