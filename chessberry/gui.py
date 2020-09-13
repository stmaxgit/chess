from typing import List, Tuple
from math import floor
from chessberry import chess
import pyglet

SQUARE_ONE_COLOR = (150, 125, 125, 255)
SQUARE_TWO_COLOR = (200, 200, 200, 255)
LEDGER_COLOR = (225, 225, 225, 255)
WINDOW_WIDTH = 512
WINDOW_HEIGHT = WINDOW_WIDTH

current_piece: chess.Piece or None = None
current_sprite: pyglet.sprite.Sprite or None = None
pieces: List[chess.Piece] = list()
sprites: List[pyglet.sprite.Sprite] = list()


def _set_current_piece_and_sprite(indices: Tuple[int, int], piece_list: List[chess.Piece],
                                  sprite_list: List[pyglet.sprite.Sprite], chess_game: chess.Game) -> bool:
    global current_piece, current_sprite
    for i, elem in enumerate(piece_list):
        if chess_game.whose_move == elem.color and elem.file == indices[0] and elem.rank == indices[1] and (
                elem in game.board):
            current_piece = elem
            current_sprite = sprite_list[i]
            return True
    return False


def _get_indices(x: int, y: int, win: pyglet.window.Window) -> Tuple[int, int]:
    return floor(x / win.width * 8), floor(y / win.height * 8)


if __name__ == '__main__':
    window = pyglet.window.Window(WINDOW_WIDTH, WINDOW_HEIGHT)
    board_image = pyglet.image.CheckerImagePattern(
       SQUARE_ONE_COLOR, SQUARE_TWO_COLOR).create_image(window.height // 4, window.height // 4)
    sprite_size = board_image.height // 2

    game = chess.Game()
    batch = pyglet.graphics.Batch()
    for piece in game.board:
        pieces.append(piece)
        sprite = pyglet.sprite.Sprite(pyglet.image.load(piece.image), batch=batch)
        sprites.append(sprite)
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


    @window.event
    def on_mouse_press(x, y, button, modifers):
        indices = _get_indices(x, y, window)
        _set_current_piece_and_sprite(indices, pieces, sprites, game)
        if isinstance(current_piece, chess.Piece) and isinstance(current_sprite, pyglet.sprite.Sprite):
            has_moved = game.move(current_piece.square, chess.from_indices(indices))
            current_sprite.position = current_piece.file * window.width // 8, current_piece.rank * window.height // 8
            if has_moved:
                last_move = game.move_ledger[len(game.move_ledger) - 1]
                if isinstance(last_move, chess.Capture):
                    idx = pieces.index(last_move.captured_alias)
                    sprites[idx].visible = False
                elif isinstance(last_move, chess.Castle):
                    idx = pieces.index(last_move.rook_alias)
                    sprites[idx].position = (
                        last_move.rook_alias.file * window.width // 8, last_move.rook_alias.rank * window.height // 8)

    pyglet.app.run()
