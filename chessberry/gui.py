from typing import List, Optional
#  from math import floor
from chessberry import chess
import pyglet


class SpritePiece:
    def __init__(self, piece: chess.ChessPiece, file: int, rank: int):
        self.piece = piece
        self.file = file
        self.rank = rank


SQUARE_ONE_COLOR = (150, 125, 125, 255)
SQUARE_TWO_COLOR = (200, 200, 200, 255)
LEDGER_COLOR = (225, 225, 225, 255)
WINDOW_WIDTH = 512
WINDOW_HEIGHT = WINDOW_WIDTH

pieces: List[Optional[chess.ChessPiece]] = []
sprites: List[pyglet.sprite.Sprite] = []

if __name__ == '__main__':
    window = pyglet.window.Window(WINDOW_WIDTH, WINDOW_HEIGHT)
    board_image = pyglet.image.CheckerImagePattern(
       SQUARE_ONE_COLOR, SQUARE_TWO_COLOR).create_image(window.height // 4, window.height // 4)
    sprite_size = board_image.height // 2

    board = chess.Board()
    batch = pyglet.graphics.Batch()

    for i, row in enumerate(board):
        for j, piece in enumerate(row):
            if piece is not None:
                pieces.append(SpritePiece(piece, j, i))
                sprites.append(pyglet.sprite.Sprite(pyglet.image.load(piece.image), batch=batch))

    for piece, sprite in zip(pieces, sprites):
        sprite.scale = sprite_size / sprite.height
        sprite.position = piece.file * WINDOW_WIDTH // 8, piece.rank * WINDOW_HEIGHT // 8

    @window.event
    def on_draw():
        window.clear()
        for x in range(4):
            for y in range(4):
                board_image.blit(window.height // 4 * x, window.height // 4 * y)
        batch.draw()

pyglet.app.run()

