import unittest

from chess1 import *


class TestEnpassant(unittest.TestCase):

    @staticmethod
    def test_enpassant_white():
        game = Game()
        game.move('e2', 'e4')
        game.move('h7', 'h5')
        game.move('e4', 'e5')
        game.move('f7', 'f5')
        assert(game['e5'].can_move_to('f6', game))

    @staticmethod
    def test_no_enpassant_white_last_move_not_black_pawn():
        game = Game()
        game.move('e2', 'e4')
        game.move('f7', 'f5')
        game.move('e4', 'e5')
        game.move('h7', 'h6')
        assert(not game['e5'].can_move_to('f6', game))

    @staticmethod
    def test_enpassant_black():
        game = Game()
        game.move('e2', 'e4')
        game.move('h7', 'h5')
        game.move('e4', 'e5')
        game.move('h5', 'h4')
        game.move('g2', 'g4')
        assert(game['h4'].can_move_to('g3', game))

    @staticmethod
    def test_no_enpassant_black_last_move_not_white_pawn():
        game = Game()
        game.move('e2', 'e4')
        game.move('h7', 'h5')
        game.move('g2', 'g4')
        game.move('h5', 'h4')
        game.move('a2', 'a3')
        assert(not game['h4'].can_move_to('g3', game))


if __name__ == '__main__':
    unittest.main()
