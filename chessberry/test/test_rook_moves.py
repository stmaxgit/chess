from chessberry.chess import *
from chessberry.test import tools


import unittest


class TestRookCanMove(unittest.TestCase):

    @staticmethod
    def test1():
        board = Board(True)
        board.attach('a1', WHITE_ROOK)
        board.attach('a7', BLACK_ROOK)
        alg_set = tools.to_alg_set(move_set('a1', board))
        assert('a7' in alg_set)
        assert('a8' not in alg_set)

    @staticmethod
    def test2():
        board = Board(True)
        board.attach('a1', WHITE_ROOK)
        board.attach('a2', WHITE_PAWN)
        board.attach('a7', BLACK_PAWN)
        alg_set = tools.to_alg_set(move_set('a1', board))
        assert('a7' not in alg_set)

    @staticmethod
    def test3():
        board = Board(True)
        board.attach('e4', WHITE_ROOK)
        board.attach('e5', WHITE_PAWN)
        board.attach('e6', BLACK_PAWN)
        board.attach('b4', WHITE_PAWN)
        board.attach('f4', BLACK_PAWN)
        ref_set = {'e1', 'e2', 'e3', 'd4', 'c4', 'f4'}
        calculated_set = tools.to_alg_set(move_set('e4', board))
        assert(calculated_set == ref_set)

    @staticmethod
    def test4():
        board = Board()
        assert(move_set('a1', board) == set())

    @staticmethod
    def test5():
        board = Board(True)
        board.attach('e2', WHITE_ROOK)
        board.attach('e3', BLACK_ROOK)
        board.attach('e1', WHITE_KING)
        ref_set = {'e3'}
        calculated_set = tools.to_alg_set(move_set('e2', board))
        assert(calculated_set == ref_set)


if __name__ == '__main__':
    unittest.main()
