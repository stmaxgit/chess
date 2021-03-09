import unittest

from chessberry.chess import *


class TestPawnCapture(unittest.TestCase):
    @staticmethod
    def test_easy():
        board = Board()
        board.move('e2', 'e4')
        board.move('d7', 'd5')
        assert(board.move('e4', 'd5'))


if __name__ == '__main__':
    unittest.main()
