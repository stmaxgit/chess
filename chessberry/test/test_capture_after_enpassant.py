import unittest

from chessberry.chess import *


class TestCapture(unittest.TestCase):
    @staticmethod
    def test():
        board = Board(False)
        board.move('e2', 'e4')
        board.move('a7', 'a6')
        board.move('e4', 'e5')
        board.move('f7', 'f5')
        assert(board.move('e5', 'f6'))
        print(board.get_piece('f6'))
        board.move('d7', 'f6')
        assert True
