WHITE = True
BLACK = not WHITE
LEFT = True
RIGHT = not LEFT
FILES_IDX = (0, 1, 2, 3, 4, 5, 6, 7)
RANKS_IDX = FILES_IDX
FILES_ALG = ('a', 'b', 'c', 'd', 'e', 'f', 'g', 'h')
RANKS_ALG = ('1', '2', '3', '4', '5', '6', '7', '8')
INDICES = set()
for _file in FILES_IDX:
    for _rank in RANKS_IDX:
        INDICES.add((_file, _rank))
ALGEBRAIC_COORDINATES = set()
for _file in FILES_ALG:
    for _rank in RANKS_ALG:
        ALGEBRAIC_COORDINATES.add(_file + _rank)


class Empty:
    def __repr__(self):
        return '...'


EMPTY = Empty()
