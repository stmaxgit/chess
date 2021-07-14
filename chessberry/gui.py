from typing import List, Tuple
from math import floor
from chessberry import chess

import pyglet

WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600
BOARD_LENGTH = 600
LIGHT_SQUARE_COLOR = (200, 200, 200, 255)
DARK_SQUARE_COLOR = (150, 125, 125, 255)
LEDGER_WIDTH = 200
LEDGER_BORDER_WIDTH = 10
LEDGER_COLOR = LIGHT_SQUARE_COLOR[0:3]
LEDGER_BORDER_COLOR = DARK_SQUARE_COLOR[0:3]


def _nearest_to_n_divides_by_m(n: int, m: int):
    #  This assumes, n, m both positive
    q = int(n / m)
    n1 = m * q
    n2 = m * (q + 1)
    if abs(n - n1) < abs(n - n2):
        return n1
    return n2


class _SpritePiece(pyglet.sprite.Sprite):
    def __init__(
        self,
        piece: chess.ChessPiece,
        file: int,
        rank: int,
        batch: pyglet.graphics.Batch,
    ):
        self.piece = piece
        self.file = file
        self.rank = rank
        super().__init__(pyglet.image.load(piece.image), batch=batch)


class BoardWindow(pyglet.window.Window):
    def __init__(
        self,
        width: int,
        height: int,
        board_length: int,
        light_square_color: Tuple[int, int, int, int],
        dark_square_color: Tuple[int, int, int, int],
        ledger_width: int,
        ledger_border_width: int,
        ledger_color: Tuple[int, int, int],
        ledger_border_color: Tuple[int, int, int],
        board: chess.Board,
        last_click: Tuple[int, int] = None,
    ):
        assert ledger_width < width, "Width of ledger must be less than total width."
        super().__init__(width, height)

        self.board_length = _nearest_to_n_divides_by_m(board_length, 8)
        self.board_image = pyglet.image.CheckerImagePattern(
            light_square_color, dark_square_color
        ).create_image(self.board_length // 4, self.board_length // 4)
        self.light_square_color = light_square_color
        self.dark_square_color = dark_square_color

        self.x_sep = (width - ledger_width - self.board_length) // 3
        self.y_sep = (height - self.board_length) // 2
        self.batch = pyglet.graphics.Batch()

        self.ledger_width = ledger_width
        self.ledger_image = pyglet.shapes.BorderedRectangle(
            2 * self.x_sep + self.board_length,
            self.y_sep,
            self.ledger_width,
            self.board_length,
            border=ledger_border_width,
            border_color=ledger_border_color,
            color=ledger_color,
            batch=self.batch,
            )

        self.board = board
        self.last_click = last_click

        self._refresh_pieces()

    def move(self, start: str, end: str):
        self.board.move(start, end)
        self._refresh_pieces()

    def _refresh_pieces(self):
        self.pieces: List[_SpritePiece] = []
        for i, row in enumerate(self.board):
            for j, p in enumerate(row):
                if p is not None:
                    self.pieces.append(_SpritePiece(p, j, i, self.batch))

        sprite_size = self.board_image.width // 2
        for p in self.pieces:
            p.scale = sprite_size / p.height
            p.position = (
                self.x_sep + p.file * self.board_length // 8,
                self.y_sep + p.rank * self.board_length // 8,
            )

    def on_draw(self):
        window.clear()
        for x in range(4):
            for y in range(4):
                self.board_image.blit(self.x_sep + self.board_length // 4 * x,
                                      self.y_sep + self.board_length // 4 * y)
        self.batch.draw()

    def on_mouse_press(self, x, y, dx, dy):
        selected = floor(8 * (y - self.y_sep) / self.board_length), floor(
            (8 * (x - self.x_sep) / self.board_length)
        )
        print(chess.move_set(chess.from_indices(selected), window.board))
        if selected in chess.INDICES and self.last_click in chess.INDICES:
            self.move(
                chess.from_indices(window.last_click), chess.from_indices(selected)
            )
        window.last_click = selected


if __name__ == "__main__":

    window = BoardWindow(
        WINDOW_WIDTH,
        WINDOW_HEIGHT,
        BOARD_LENGTH,
        LIGHT_SQUARE_COLOR,
        DARK_SQUARE_COLOR,
        LEDGER_WIDTH,
        LEDGER_BORDER_WIDTH,
        LEDGER_COLOR[0:3],
        LEDGER_BORDER_COLOR[0:3],
        chess.Board(),
    )

pyglet.app.run()
