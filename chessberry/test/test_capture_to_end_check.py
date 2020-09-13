import unittest

from chess1 import *


class TestPawnCapture(unittest.TestCase):
    @staticmethod
    def test_enpassant_out_of_check():
        board = Board()
        board.attach(King('e8', BLACK))
        board.attach(Pawn('e7', BLACK))
        board.attach(Knight('e4', WHITE))
        game = Game(board)
        game.move('e4', 'f6')
        assert(game.move('e7', 'f6'))


if __name__ == '__main__':
    unittest.main()
