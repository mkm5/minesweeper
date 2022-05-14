from collections import deque
from enum import Enum, auto
from dataclasses import dataclass
from itertools import product
from random import sample

from typing import Generator, List, Set, Tuple

from difficulty import Difficulties

@dataclass
class Tile:
    row: int
    col: int
    bombsInNeighbor: int = 0
    isBomb: bool = False
    isFlagged: bool = False
    isRevealed: bool = False

class State(Enum):
    ONGOING = auto()
    WIN = auto()
    LOSE = auto()

class Minesweeper:
    def __init__(self, difficulty: Difficulties) -> None:
        self._state: State = State.ONGOING
        self._difficulty = difficulty
        self._bombs: Set[Tuple[int, int]] = self._generateBombs()
        self._flags: int = 0
        self._grid: List[List[Tile]] = self._generateGrid()

    @property
    def state(self) -> State:
        return self._state

    @property
    def bombs(self) -> Set[Tuple[int, int]]:
        return self._bombs

    # NOTE: only for test purpose
    def __str__(self) -> str:
        out = f'Minesweeper {self._difficulty.name}\n'
        out += f'rows={self._difficulty.rows} cols={self._difficulty.cols} bombs={self._difficulty.bombs}\n'
        out += str(self._bombs) + '\n'
        for row in self._grid:
            for tile in row:
                if tile.isBomb and not tile.isFlagged: out += 'B '
                elif not tile.isBomb and tile.isFlagged: out += 'F '
                elif tile.isBomb and tile.isFlagged: out += 'X '
                else:
                    if tile.bombsInNeighbor > 0: out += f'{tile.bombsInNeighbor} '
                    else: out += '_ '
            out += '\n'
        return out

    def _generateBombs(self) -> Set[Tuple[int, int]]:
        rows, cols = self._difficulty.rows, self._difficulty.cols
        nbombs = self._difficulty.bombs
        return set(sample(tuple(product(range(rows), range(cols))), nbombs))

    def _getNeighborsPosition(self, row: int, col: int) -> Generator[Tuple[int, int], None, None]:
        max_rows = self._difficulty.rows
        max_cols = self._difficulty.cols

        rows_range = (row - 1, row, row + 1)
        cols_range = (col - 1, col, col + 1)
        for nrow, ncol in product(rows_range, cols_range):
            if row == nrow and col == ncol: continue
            if (nrow < max_rows and nrow >= 0) and (ncol < max_cols and ncol >= 0):
                yield nrow, ncol

    def _generateGrid(self) -> List[List[Tile]]:
        grid: List[List[Tile]] = [
            [Tile(row, col) for col in range(self._difficulty.cols)]
            for row in range(self._difficulty.rows)
        ]

        for row, col in self._bombs:
            grid[row][col].isBomb = True
            for nrow, ncol in self._getNeighborsPosition(row, col):
                grid[nrow][ncol].bombsInNeighbor += 1
        return grid

    def _checkIfAllBombsAreFlagged(self) -> bool:
        return all((self._grid[trow][tcol].isFlagged for trow, tcol in self._bombs))

    def toggleFlag(self, row: int, col: int) -> bool:
        if self._state != State.ONGOING:
            raise ValueError('cant change state after game ended')

        tile = self._grid[row][col]
        if tile.isRevealed:
            raise ValueError('cant flag revealed tile')

        tile.isFlagged = not tile.isFlagged
        self._flags += 1 if tile.isFlagged else -1
        if tile.isFlagged:
            if (
                self._flags == self._difficulty.bombs \
                and self._checkIfAllBombsAreFlagged()
            ): self._state = State.WIN
        return tile.isFlagged

    def reveal(self, row: int, col: int) -> List[Tile]:
        if self._state != State.ONGOING:
            raise ValueError('cant change state after game ended')

        tile = self._grid[row][col]
        if tile.isBomb:
            self._state = State.LOSE
            return []

        if tile.isRevealed:
            return []

        tile.isRevealed = True
        changed_tiles = [tile]

        if tile.bombsInNeighbor:
            return changed_tiles

        queue = deque([(tile.row, tile.col)])
        while len(queue) != 0:
            row, col = queue.popleft()
            for nrow, ncol in self._getNeighborsPosition(row, col):
                ntile = self._grid[nrow][ncol]
                if any((ntile.isBomb, ntile.isFlagged, ntile.isRevealed)):
                    continue

                if ntile.bombsInNeighbor == 0:
                    queue.append((ntile.row, ntile.col))

                ntile.isRevealed = True
                changed_tiles.append(ntile)

        return changed_tiles

if __name__ == '__main__':
    print(Minesweeper(Difficulties.EASY))
