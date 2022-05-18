import platform
from functools import partial
from tkinter import RAISED, DISABLED, SUNKEN
from tkinter import Button, Frame, Menu, Tk, messagebox
from typing import Callable, NoReturn

from difficulty import *
from logic import Minesweeper, State

LEFT_CLICK = '<Button-1>'
RIGHT_CLICK = '<Button-3>' if not platform.system() == 'Darwin' else '<Button-2>'

BUTTON_APPEARANCES = {
    'default': { 'text': ' ', 'bg': 'SystemButtonFace', 'fg': 'SystemButtonText', 'relief': RAISED },
    'revealed': { 'disabledforeground': 'SystemButtonText', 'state': DISABLED, 'relief': SUNKEN },
    'flagged': { 'text': 'F', 'fg': '#9B59B6' },
    'bomb': { 'text': 'B', 'disabledforeground': '#E74C3C', 'state': DISABLED, 'relief': SUNKEN }
}

class GameManager:
    def __init__(self, on_win: Callable[[], None], on_lose: Callable[[], None]):
        self._difficulty: Difficulty = EASY
        self._minesweeper: Minesweeper = None
        self._onWin: Callable[[], None] = on_win
        self._onLose: Callable[[], None] = on_lose

    def _revealAllBombs(self, frame: Frame) -> None:
        for brow, bcol in self._minesweeper.bombs:
            bomb_btn = frame.grid_slaves(row=brow, column=bcol)[0]
            bomb_btn.configure(**BUTTON_APPEARANCES['bomb'])

    def reveal(self, btn: Button, row: int, col: int, *args) -> None:
        changed_tiles = self._minesweeper.reveal(row, col)

        frame = btn._nametowidget(btn.winfo_parent())
        for tile in changed_tiles:
            tbtn = frame.grid_slaves(row=tile.row, column=tile.col)[0]
            text = str(tile.bombsInNeighbor) if tile.bombsInNeighbor else ' '
            tbtn.configure(text=text, **BUTTON_APPEARANCES['revealed'])

        if self._minesweeper.state == State.LOSE:
            self._revealAllBombs(frame)
            self._onLose()

    def toggleFlag(self, btn: Button, row: int, col: int, *args) -> None:
        try:
            btn.configure(
                **BUTTON_APPEARANCES[
                    'flagged' if self._minesweeper.toggleFlag(row, col) else 'default'
                ]
            )
            if self._minesweeper.state == State.WIN:
                self._onWin()
        except ValueError:
            # We can ignore if user tries to click on disabled element (for now)
            pass

    def newGame(self) -> None:
        self._minesweeper = Minesweeper(self._difficulty)

    def setDifficulty(self, difficulty: Difficulty) -> None:
        self._difficulty = difficulty


class App:
    def __init__(self) -> None:
        self._root = Tk()
        self._root.title('Minesweeper')
        self._root.resizable(False, False)

        self._game_manager = GameManager(self._onWin, self._onLose)

        self._game_frame = Frame(self._root)
        self._game_frame.pack()

        self._menu = Menu(self._root)
        self._menu.add_command(label='New Game', command=self._newGame)

        self._difficul_menu = Menu(self._menu, tearoff=False)
        for difficulty in (EASY, MEDIUM, HARD):
            self._difficul_menu.add_command(
                label=difficulty.name.title(),
                command=partial(self._setDifficulty, difficulty)
            )

        self._menu.add_cascade(label='Difficulty', menu=self._difficul_menu)

        self._root.config(menu=self._menu)

    def _setup(self) -> None:
        rows = self._game_manager._difficulty.rows
        cols = self._game_manager._difficulty.cols
        for row in range(rows):
            for col in range(cols):
                element = Button(self._game_frame, text=' ', height=1, width=2, borderwidth=1)
                element.bind(LEFT_CLICK, partial(self._game_manager.reveal, element, row, col))
                element.bind(RIGHT_CLICK, partial(self._game_manager.toggleFlag, element, row, col))
                element.grid(row=row, column=col)

    def _cleanGameFrame(self) -> None:
        for widget in self._game_frame.winfo_children():
            widget.destroy()

    def _newGame(self):
        self._cleanGameFrame()
        self._game_manager.newGame()
        self._setup()

    def _setDifficulty(self, difficulty: Difficulty) -> None:
        self._game_manager.setDifficulty(difficulty)
        self._newGame()

    def _onLose(self) -> None:
        if messagebox.showinfo('Game Over', 'You lost!'):
            self._newGame()

    def _onWin(self) -> None:
        if messagebox.showinfo('', 'You won!'):
            self._newGame()

    def run(self) -> NoReturn:
        self._newGame()
        self._root.mainloop()

if __name__ == '__main__':
    App().run()

