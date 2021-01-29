from chess1 import *


import unittest


class TestRookCanMove(unittest.TestCase):

    @staticmethod
    def test_easy_white():
        board = Board()
        board.attach(Rook('a1', WHITE))
        board.attach(Pawn('a7', BLACK))
        game = Game(board)
        assert(game['a1'].can_move_to('a7', game))

    @staticmethod
    def test_one_square_moved():
        board = Board()
        board.attach(Rook('d8', WHITE))
        game = Game(board)
        assert(game['d8'].can_move_to('d7', game))

    @staticmethod
    def test_blocked_white():
        board = Board()
        board.attach(Rook('a1', WHITE))
        board.attach(Pawn('a2', WHITE))
        board.attach(Pawn('a7', BLACK))
        game = Game(board)
        assert(not game['a1'].can_move_to('a7', game))

    @staticmethod
    def test_easy_black():
        board = Board()
        board.attach(Rook('e5', BLACK))
        board.attach(Pawn('a5', WHITE))
        game = Game(board)
        assert(not game['e5'].can_move_to('a7', game))

    @staticmethod
    def test_easy_return_false():
        board = Board()
        board.attach(Rook('e5', BLACK))
        game = Game(board)
        assert(not game['e5'].can_move_to('a1', game))


if __name__ == '__main__':
    unittest.main()
