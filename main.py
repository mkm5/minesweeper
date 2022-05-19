import platform
from functools import partial
from tkinter import (
    BUTT, Entry, Event, Label, PhotoImage, Toplevel,
    Button, Frame, Menu, Tk, messagebox
)
from tkinter.font import Font, nametofont
from typing import Callable, NoReturn

from difficulty import Difficulty, EASY, MEDIUM, HARD
from logic import Minesweeper, State

LEFT_CLICK = '<Button-1>'
RIGHT_CLICK = '<Button-3>' if not platform.system() == 'Darwin' else '<Button-2>'

APPEARANCES = {
    'text': {
        'image': '',
        'font': None,
        'compound': 'center',
        'bg': 'SystemButtonFace', 'fg': 'SystemButtonText',
        'height': 1, 'width': 2, 'borderwidth': 1, 'padx': 2
    },
    'image': { 'text': '', 'height': 20, 'width': 20, 'padx': 0 },
    'default': { 'text': ' ', 'relief': 'raised' },
    'reveald': { 'state': 'disabled', 'relief': 'sunken' },
    'flagged': { 'image': None },
    'bomb': { 'image': None, 'bg': '#E74C3C' }
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
            Label(frame, text=f'{entry.title()}:', width=10, anchor='w', justify='left').pack(side='left')
            self._entries[entry] = Entry(frame)
            self._entries[entry].pack(side='right', expand=1, fill='x')
            frame.pack(side='top', expand=1, fill='x')

        confirm_btn = Button(self, text='Confirm', command=self._onConfirm)
        confirm_btn.pack(side='right')

    def _onConfirm(self) -> None:
        try:
            rows = int(self._entries['rows'].get())
            cols = int(self._entries['cols'].get())
            bombs = int(self._entries['bombs'].get())
        except ValueError:
            messagebox.showerror(
                'Invalid type!',
                'At least one of the entries contains invalid data type.'
            )
            return
        if rows == 0 or cols == 0 or bombs == 0:
            messagebox.showerror(
                'Invalid value!',
                'At least one of the entries conains invalid value.'
            )
            return
        if rows * cols <= bombs:
            messagebox.showerror(
                'Invalid value!',
                'Number of bombs is too high for provided grid size.'
            )
            return

        self.destroy()
        self._change_difficulty(Difficulty('custom', rows, cols, bombs))


class App:
    def __init__(self) -> None:
        self._difficulty: Difficulty = EASY
        self._minesweeper: Minesweeper = None

        self._root = Tk()
        self._root.title('Minesweeper')
        self._root.resizable(False, False)

        APPEARANCES['flagged']['image'] = PhotoImage(name='flag', file='./img/flag.png')
        APPEARANCES['bomb']['image'] = PhotoImage(name='bomb', file='./img/bomb.png')
        APPEARANCES['text']['font'] = nametofont('TkFixedFont')
        if platform.system() == 'Windows':
            APPEARANCES['text']['font'] = Font(family='Consolas', size=10)

        self._game_frame = Frame(self._root)
        self._game_frame.pack()

        self._menu = Menu(self._root)
        self._menu.add_command(label='New Game', command=self._newGame)

        self._difficul_menu = Menu(self._menu, tearoff=False)
        for difficulty in (EASY, MEDIUM, HARD):
            self._difficul_menu.add_command(
                label=difficulty.name.title(),
                command=partial(self._setDifficulty, difficulty),
            )
        self._difficul_menu.add_command(
            label='Custom difficulty',
            command=partial(CustomDifficultyDialog, self._setDifficulty),
        )

        self._menu.add_cascade(label='Difficulty', menu=self._difficul_menu)

        self._root.config(menu=self._menu)

    def _setup(self) -> None:
        rows = self._difficulty.rows
        cols = self._difficulty.cols
        for row in range(rows):
            for col in range(cols):
                element = Button(self._game_frame, **APPEARANCES['text'], **APPEARANCES['default'])
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
            bomb_btn.configure(**APPEARANCES['image'], **APPEARANCES['bomb'])

    def _reveal(self, row: int, col: int, _: Event) -> None:
        changed_tiles = self._minesweeper.reveal(row, col)
        for tile in changed_tiles:
            btn = self._game_frame.grid_slaves(row=tile.row, column=tile.col)[0]
            text = str(tile.bombsInNeighbor) if tile.bombsInNeighbor else ' '
            btn.configure(text=text, **APPEARANCES['text'], **APPEARANCES['reveald'])

        if self._minesweeper.state == State.LOSE:
            self._revealBombs()
            self._onLose()

    def _toggleFlag(self, row: int, col: int, event: Event) -> None:
        btn = event.widget
        try:
            is_flagged = self._minesweeper.toggleFlag(row, col)
            if is_flagged:
                btn.configure(**APPEARANCES['image'], **APPEARANCES['flagged'])
            else:
                btn.configure(**APPEARANCES['text'], **APPEARANCES['default'])
            if self._minesweeper.state == State.WIN:
                self._onWin()
        except ValueError:  # Will occure if already revealed tile is getting flagged
            pass

    def run(self) -> NoReturn:
        self._newGame()
        self._root.mainloop()


if __name__ == '__main__':
    App().run()
