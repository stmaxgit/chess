import unittest

from chessberry.chess import *


class TestEnpassant(unittest.TestCase):

    @staticmethod
    def test_enpassant_white():
        board = Board()
        board.move('e2', 'e4')
        board.move('h7', 'h5')
        board.move('e4', 'e5')
        board.move('f7', 'f5')
        assert(board.move('e5', 'f6'))

    @staticmethod
    def test_no_enpassant_white_last_move_not_black_pawn():
        board = Board()
        board.move('e2', 'e4')
        board.move('f7', 'f5')
        board.move('e4', 'e5')
        board.move('h7', 'h6')
        assert(not board.move('e5', 'f6'))

    @staticmethod
    def test_enpassant_black():
        board = Board()
        board.move('e2', 'e4')
        board.move('h7', 'h5')
        board.move('e4', 'e5')
        board.move('h5', 'h4')
        board.move('g2', 'g4')
        assert(board.move('h4', 'g3'))

    @staticmethod
    def test_no_enpassant_black_last_move_not_white_pawn():
        board = Board()
        board.move('e2', 'e4')
        board.move('h7', 'h5')
        board.move('g2', 'g4')
        board.move('h5', 'h4')
        board.move('a2', 'a3')
        assert(not board.move('h4', 'g3'))


if __name__ == '__main__':
    unittest.main()
