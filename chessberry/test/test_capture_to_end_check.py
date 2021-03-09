import unittest

from chessberry.chess import *


class TestPawnCapture(unittest.TestCase):
    @staticmethod
    def test_enpassant_out_of_check():
        board = Board(True)
        board.attach('e8', BLACK_KING)
        board.attach('e7', BLACK_PAWN)
        board.attach('e4', WHITE_KNIGHT)


if __name__ == '__main__':
    unittest.main()
