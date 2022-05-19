from dataclasses import dataclass


@dataclass
class Difficulty:
    name: str
    rows: int
    cols: int
    bombs: int


EASY = Difficulty('easy', 9, 9, 10)
MEDIUM = Difficulty('medium', 16, 16, 40)
HARD = Difficulty('hard', 16, 30, 99)
