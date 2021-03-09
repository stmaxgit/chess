import unittest

from chessberry.chess import *


class TestPin(unittest.TestCase):

    @staticmethod
    def test_pinned_easy():
        board = Board(True)
        board.attach('e1', WHITE_KING)
        board.attach('e8', BLACK_KING)
        board.attach('e2', WHITE_ROOK)
        board.attach('e7', BLACK_ROOK)
        assert(not board.move('e2', 'a2'))


if __name__ == '__main__':
    unittest.main()
