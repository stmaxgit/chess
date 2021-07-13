from typing import List, Tuple
from math import floor
from chessberry import chess

import pyglet

WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600
BOARD_LENGTH = 500
LIGHT_SQUARE_COLOR = (200, 200, 200, 255)
DARK_SQUARE_COLOR = (150, 125, 125, 255)
LEDGER_WIDTH = 125
LEDGER_COLOR = LIGHT_SQUARE_COLOR


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
        ledger_color: Tuple[int, int, int, int],
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
        self.ledger_image = pyglet.shapes.Rectangle(
            2 * self.x_sep + self.board_length,
            self.y_sep,
            self.ledger_width,
            self.board_length,
            ledger_color[0:3],
            batch=self.batch,
            )
        self.ledger_color = ledger_color

        self.board = board
        self.last_click = last_click

        self.pieces: List[_SpritePiece] = []
        for i, row in enumerate(self.board):
            for j, p in enumerate(row):
                if p is not None:
                    self.pieces.append(_SpritePiece(p, j, i, self.batch))

        sprite_size = self.board_image.width // 2
        for p in self.pieces:
            p.scale = sprite_size / p.height
            self._update_position(p)

    def move(self, start: str, end: str) -> bool:
        if self.board.move(start, end):
            start_rank, start_file = chess.to_indices(start)
            end_rank, end_file = chess.to_indices(end)
            for piece in self.pieces:
                #  Piece on start file that has already satisfied move criteria
                if piece.file == start_file and piece.rank == start_rank:
                    #  If capturing something, need to remove captured piece from board
                    if self.board.ledger[len(self.board.ledger) - 1].capture:
                        self._handle_capture(end_rank, end_file)
                    # If castling, need to update rook position as well
                    if self.board.ledger[len(self.board.ledger) - 1].castle:
                        self._handle_castle(end_rank)

                    piece.rank, piece.file = end_rank, end_file
                    self._update_position(piece)
                    return True
        return False

    def _handle_capture(self, end_rank: int, end_file: int):
        """If a piece is captured, the sprite needs to be made invisible and the piece
        removed from the reference list.
        """
        for piece in self.pieces:
            if piece.file == end_file and piece.rank == end_rank:
                self.pieces.remove(piece)
                piece.visible = False
                return
        #  Must be enpassant capture at this point.
        if self.board.turn != chess.Color.LIGHT:
            for piece in self.pieces:
                if piece.file == end_file and piece.rank == end_rank - 1:
                    self.pieces.remove(piece)
                    piece.visible = False
                    return
        else:
            for piece in self.pieces:
                if piece.file == end_file and piece.rank == end_rank + 1:
                    self.pieces.remove(piece)
                    piece.visible = False
                    return

    def _handle_castle(self, end_file: int):
        """If castling, the appropriate rook needs to be updated."""
        #  This method will be called after the turn has already been updated,
        #  so we check against the opposite color of what you would anticipate.
        if self.board.turn != chess.Color.LIGHT:
            if end_file == 2:
                for piece in self.pieces:
                    if piece.rank == 0 and piece.file == 0:
                        piece.file = 3
                        self._update_position(piece)
                        return
            else:
                for piece in self.pieces:
                    if piece.rank == 0 and piece.file == 7:
                        piece.file = 5
                        self._update_position(piece)
                        return
        else:
            if end_file == 2:
                for piece in self.pieces:
                    if piece.rank == 7 and piece.file == 0:
                        piece.file = 3
                        self._update_position(piece)
                        return
            else:
                for piece in self.pieces:
                    if piece.rank == 7 and piece.file == 7:
                        piece.file = 5
                        self._update_position(piece)
                        return

    def _update_position(self, piece: _SpritePiece):
        """Update position instance variable for the passed piece."""
        piece.position = (
            self.x_sep + piece.file * self.board_length // 8,
            self.y_sep + piece.rank * self.board_length // 8,
        )

    def on_draw(self):
        window.clear()
        for x in range(4):
            for y in range(4):
                self.board_image.blit(self.x_sep + self.board_length // 4 * x, self.y_sep + self.board_length // 4 * y)
        self.batch.draw()

    def on_mouse_press(self, x, y, dx, dy):
        selected = floor(8 * (y - self.y_sep) / self.board_length), floor(
            (8 * (x - self.x_sep) / self.board_length)
        )
        if self.last_click is not None:
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
        LEDGER_COLOR,
        chess.Board(),
    )

pyglet.app.run()
