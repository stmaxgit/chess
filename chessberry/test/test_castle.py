import unittest

from chessberry.chess import *
from chessberry.test import tools


class TestCastle(unittest.TestCase):
    @staticmethod
    def test_white_castle_easy():
        board = Board(True)
        board.attach('a1', WHITE_ROOK)
        board.attach('h1', WHITE_ROOK)
        board.attach('e1', WHITE_KING)
        board.attach('f8', BLACK_ROOK)
        assert('c1' in tools.to_alg_set(move_set('e1', board)))
        assert('g1' not in tools.to_alg_set(move_set('e1', board)))

    @staticmethod
    def test_black_castle_easy():
        board = Board(True)
        board.attach('a8', BLACK_ROOK)
        board.attach('h8', BLACK_ROOK)
        board.attach('e8', BLACK_KING)
        board.attach('d8', WHITE_ROOK)
        assert('g8' not in tools.to_alg_set(move_set('e8', board)))
        assert('c8' not in tools.to_alg_set(move_set('e8', board)))

    @staticmethod
    def test_black_castle_easy2():
        board = Board(True, Color.DARK)
        board.attach('a8', BLACK_ROOK)
        board.attach('h8', BLACK_ROOK)
        board.attach('e8', BLACK_KING)
        board.attach('d1', WHITE_ROOK)
        assert('g8' in tools.to_alg_set(move_set('e8', board)))
        assert('c8' not in tools.to_alg_set(move_set('e8', board)))

    @staticmethod
    def test_white_castle_obstructed():
        board = Board(True)
        board.attach('a1', WHITE_ROOK)
        board.attach('b1', WHITE_KNIGHT)
        board.attach('e1', WHITE_KING)
        board.attach('f1', WHITE_BISHOP)
        board.attach('h1', WHITE_ROOK)
        assert('g1' not in tools.to_alg_set(move_set('e1', board)))
        assert('c1' not in tools.to_alg_set(move_set('e1', board)))


if __name__ == '__main__':
    unittest.main()
