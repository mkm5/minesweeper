from enum import Enum
from dataclasses import dataclass

from typing import Tuple

@dataclass
class Difficulty:
    name: str; rows: int ;cols: int; bombs: int

class Difficulties(Enum):
    EASY = Difficulty('easy', 9, 9, 10)
    MEDIUM = Difficulty('medium', 16, 16, 40)
    HARD = Difficulty('hard', 16, 30, 99)

    @classmethod
    def getAllDifficulties(cls) -> Tuple['Difficulties']:
        return (
            getattr(cls, v) for v in filter(lambda x: not x.startswith('__'), dir(cls))
        )

    @property
    def rows(self) -> int:
        return self.value.rows

    @property
    def cols(self) -> int:
        return self.value.cols

    @property
    def bombs(self) -> int:
        return self.value.bombs
