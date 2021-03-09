from typing import List, Optional, Tuple
from math import floor
from chessberry import chess
import pyglet


class SpritePiece(pyglet.sprite.Sprite):
    def __init__(self, piece: chess.ChessPiece, file: int, rank: int, batch: pyglet.graphics.Batch):
        self.piece = piece
        self.file = file
        self.rank = rank
        super().__init__(pyglet.image.load(piece.image), batch=batch)


class BoardWindow(pyglet.window.Window):
    def __init__(self, width: int, height: int,  board: chess.Board,
                 batch: pyglet.graphics.Batch, last_click: Tuple[int, int] = None):
        super().__init__(width, height)
        self.board = board
        self.batch = batch
        self.last_click = last_click


if __name__ == '__main__':
    SQUARE_ONE_COLOR = (150, 125, 125, 255)
    SQUARE_TWO_COLOR = (200, 200, 200, 255)
    LEDGER_COLOR = (225, 225, 225, 255)
    WINDOW_WIDTH = 512
    WINDOW_HEIGHT = WINDOW_WIDTH

    pieces: List[Optional[chess.ChessPiece]] = []

    window = BoardWindow(WINDOW_WIDTH, WINDOW_HEIGHT, chess.Board(), pyglet.graphics.Batch())
    board_image = pyglet.image.CheckerImagePattern(
       SQUARE_ONE_COLOR, SQUARE_TWO_COLOR).create_image(window.height // 4, window.height // 4)
    sprite_size = board_image.height // 2

    for i, row in enumerate(window.board):
        for j, p in enumerate(row):
            if p is not None:
                pieces.append(SpritePiece(p, j, i, window.batch))

    for p in pieces:
        p.scale = sprite_size / p.height
        p.position = p.file * WINDOW_WIDTH // 8, p.rank * WINDOW_HEIGHT // 8

    @window.event
    def on_draw():
        window.clear()
        for x in range(4):
            for y in range(4):
                board_image.blit(window.height // 4 * x, window.height // 4 * y)
        window.batch.draw()

    @window.event
    def on_mouse_press(x, y, dx, dy):
        selected = floor(8 * y / window.height), floor(8 * x / window.width)
        if window.last_click is not None:
            window.board.move(chess.from_indices(window.last_click), chess.from_indices(selected))
        window.last_click = selected


pyglet.app.run()
