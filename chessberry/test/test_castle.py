import unittest

from chess1 import *


class TestCastle(unittest.TestCase):
    @staticmethod
    def test_castle_easy():
        board = Board()
        board.attach(King('e1', WHITE))
        board.attach(Rook('a1', WHITE))
        game = Game(board)
        game.move('e1', 'c1')
        assert(board.__white_king.square == 'c1')
        assert(board.__white_king.indices == (2, 0))
        assert(board.__white_rooks[0].square == 'd1')
        assert(board.__white_rooks[0].indices == (3, 0))


if __name__ == '__main__':
    unittest.main()
