import unittest

from chess1 import *


class TestPin(unittest.TestCase):

    @staticmethod
    def test_pinned_easy():
        board = Board()
        board.attach(King('e1', WHITE))
        board.attach(King('e8', BLACK))
        board.attach(Rook('e2', WHITE))
        board.attach(Rook('e7', BLACK))
        game = Game(board)
        assert(not game['e2'].can_move_to('a2', game))


if __name__ == '__main__':
    unittest.main()
