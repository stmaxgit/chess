import unittest

from chessberry.chess import *


class TestPawn(unittest.TestCase):
    @staticmethod
    def test_g_file_two_push():
        b = Board()
        assert(b.move('g2', 'g4'))
