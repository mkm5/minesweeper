import platform
from functools import partial
from tkinter import LEFT, RAISED, DISABLED, RIGHT, SUNKEN, TOP, X, YES, Entry, Event, Label, Toplevel
from tkinter import Button, Frame, Menu, Tk, messagebox
from typing import Callable, NoReturn

from difficulty import Difficulty, EASY, MEDIUM, HARD
from logic import Minesweeper, State

LEFT_CLICK = '<Button-1>'
RIGHT_CLICK = '<Button-3>' if not platform.system() == 'Darwin' else '<Button-2>'

BUTTON_APPEARANCES = {
    'default': { 'text': ' ', 'bg': 'SystemButtonFace', 'fg': 'SystemButtonText', 'relief': RAISED },
    'revealed': { 'disabledforeground': 'SystemButtonText', 'state': DISABLED, 'relief': SUNKEN },
    'flagged': { 'text': 'F', 'fg': '#9B59B6' },
    'bomb': { 'text': 'B', 'disabledforeground': '#E74C3C', 'state': DISABLED, 'relief': SUNKEN }
}


class CustomDifficultyDialog(Toplevel):
    def __init__(self, change_difficulty: Callable[[Difficulty], None], *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._change_difficulty = change_difficulty

        self.title('Custom Difficulty Dialog')
        self.resizable(False, False)

        self._entries = {'rows': None, 'cols': None, 'bombs': None}
        for entry in self._entries.keys():
            frame = Frame(self)
            Label(frame, text=f'{entry.title()}:', width=10, anchor='w', justify=LEFT).pack(side=LEFT)
            self._entries[entry] = Entry[frame]
            self._entries[entry].pack(side=RIGHT, expand=YES, fill=X)
            frame.pack(side=TOP, expand=YES, fill=X)

        confirm_btn = Button(self, text='Confirm', command=self._onConfirm)
        confirm_btn.pack(side=RIGHT)

    def _onConfirm(self) -> None:
        try:
            rows = int(self._rows.get())
            cols = int(self._cols.get())
            bombs = int(self._bombs.get())
        except ValueError:
            messagebox.showerror('Invalid type!', 'At least one of the entries contains invalid data type.'); return
        if rows == 0 or cols == 0 or bombs == 0: messagebox.showerror('Invalid value!', 'At least one of the entries conains invalid value.'); return
        if rows * cols <= bombs: messagebox.showerror('Invalid value!', 'Number of bombs is too high for provided grid size.'); return

        self.destroy()
        self._change_difficulty(Difficulty('custom', rows, cols, bombs))


class App:
    def __init__(self) -> None:
        self._difficulty: Difficulty = EASY
        self._minesweeper: Minesweeper = None

        self._root = Tk()
        self._root.title('Minesweeper')
        self._root.resizable(False, False)

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
        self._difficul_menu.add_command(
            label='Custom difficulty',
            command=partial(CustomDifficultyDialog, self._setDifficulty)
        )

        self._menu.add_cascade(label='Difficulty', menu=self._difficul_menu)

        self._root.config(menu=self._menu)

    def _setup(self) -> None:
        rows = self._difficulty.rows
        cols = self._difficulty.cols
        for row in range(rows):
            for col in range(cols):
                element = Button(self._game_frame, text=' ', height=1, width=2, borderwidth=1)
                element.bind(LEFT_CLICK, partial(self._reveal, row, col))
                element.bind(RIGHT_CLICK, partial(self._toggleFlag, row, col))
                element.grid(row=row, column=col)

    def _cleanGameFrame(self) -> None:
        for widget in self._game_frame.winfo_children():
            widget.destroy()

    def _newGame(self):
        self._cleanGameFrame()
        self._minesweeper = Minesweeper(self._difficulty)
        self._setup()

    def _setDifficulty(self, difficulty: Difficulty) -> None:
        self._difficulty = difficulty
        self._newGame()

    def _onLose(self) -> None:
        if messagebox.showinfo('Game Over', 'You lost!'):
            self._newGame()

    def _onWin(self) -> None:
        if messagebox.showinfo('', 'You won!'):
            self._newGame()

    def _revealBombs(self):
        for row, col in self._minesweeper.bombs:
            bomb_btn = self._game_frame.grid_slaves(row=row, column=col)[0]
            bomb_btn.configure(**BUTTON_APPEARANCES['bomb'])

    def _reveal(self, row: int, col: int, _: Event) -> None:
        changed_tiles = self._minesweeper.reveal(row, col)
        for tile in changed_tiles:
            btn = self._game_frame.grid_slaves(row=tile.row, column=tile.col)[0]
            text = str(tile.bombsInNeighbor) if tile.bombsInNeighbor else ' '
            btn.configure(text=text, **BUTTON_APPEARANCES['revealed'])

        if self._minesweeper.state == State.LOSE:
            self._revealBombs()
            self._onLose()

    def _toggleFlag(self, row: int, col: int, event: Event) -> None:
        btn = event.widget
        try:
            btn.configure(
                **BUTTON_APPEARANCES[
                    'flagged' if self._minesweeper.toggleFlag(row, col) else 'default'
                ]
            )
            if self._minesweeper.state == State.WIN:
                self._onWin()
        except ValueError: # Will occure if already revealed tile is getting flagged
            pass

    def run(self) -> NoReturn:
        self._newGame()
        self._root.mainloop()


if __name__ == '__main__':
    App().run()
