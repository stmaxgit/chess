import unittest

from chessberry.chess import *
from chessberry.test import tools


class TestBishopCanMove(unittest.TestCase):

    @staticmethod
    def test_easy():
        board = Board(True)
        board.attach('c1', WHITE_BISHOP)
        board.attach('d2', BLACK_PAWN)
        assert('d2' in tools.to_alg_set(move_set('c1', board)))

    @staticmethod
    def test_blocked():
        board = Board(True)
        board.attach('a8', BLACK_BISHOP)
        board.attach('d5', BLACK_PAWN)
        board.attach('e4', WHITE_QUEEN)
        assert('e4' not in tools.to_alg_set(move_set('a8', board)))


if __name__ == '__main__':
    unittest.main()
