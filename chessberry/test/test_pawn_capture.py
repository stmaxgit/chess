import unittest

from chess1 import *


class TestPawnCapture(unittest.TestCase):
    @staticmethod
    def test_easy():
        game = Game()
        game.move('e2', 'e4')
        game.move('d7', 'd5')


if __name__ == '__main__':
    unittest.main()
