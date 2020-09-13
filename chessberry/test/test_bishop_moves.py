import unittest

from chess1 import *


class TestBishopCanMove(unittest.TestCase):

    @staticmethod
    def test_easy():
        board = Board()
        board.attach(Bishop('c1', WHITE))
        board.attach(Pawn('d2', BLACK))
        game = Game(board)
        assert(game['c1'].can_move_to_no_self_check_test('d2', game))

    @staticmethod
    def test_blocked():
        board = Board()
        board.attach(Bishop('a8', BLACK))
        board.attach(Pawn('d5', BLACK))
        board.attach(Queen('e4', WHITE))
        game = Game(board)
        assert(not game['a8'].can_move_to_no_self_check_test('e4', game))

    @staticmethod
    def test_other_way():
        board = Board()
        board.attach(Bishop('f1', WHITE))
        game = Game(board)
        assert(game['f1'].can_move_to_no_self_check_test('d3', game))


if __name__ == '__main__':
    unittest.main()
