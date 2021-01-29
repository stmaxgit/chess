from collections import namedtuple
from copy import copy
from enum import Enum, auto
from typing import List, Set, Tuple, Optional

""" Indices set allows for quick membership checks for out of range (off the board) moves.
"""
RANKS: List[int] = [_ for _ in range(0, 8)]
FILES: List[int] = RANKS
INDICES: Set[Tuple[int, int]] = set()
for _ in RANKS:
    for __ in FILES:
        INDICES.add((_, __))


class Piece(Enum):
    PAWN = auto()
    ROOK = auto()
    KNIGHT = auto()
    BISHOP = auto()
    QUEEN = auto()
    KING = auto()


class Color(Enum):
    WHITE = auto()
    BLACK = auto()


""" Using named tuples for the chess pieces restricts mutability concerns to the Board class and the GUI. 
    There is no practical reason for a chess piece to know rank and file information; the board keeps track of it.
"""

ChessPiece = namedtuple("ChessPiece", ["piece", "color", "value", "image"])

WHITE_PAWN = ChessPiece(Piece.PAWN, Color.WHITE, 1, "assets/Chess_plt45.png")
BLACK_PAWN = ChessPiece(Piece.PAWN, Color.BLACK, 1, "assets/Chess_pdt45.png")
WHITE_ROOK = ChessPiece(Piece.ROOK, Color.WHITE, 5, "assets/Chess_rlt45.png")
BLACK_ROOK = ChessPiece(Piece.ROOK, Color.BLACK, 5, "assets/Chess_rdt45.png")
WHITE_KNIGHT = ChessPiece(Piece.KNIGHT, Color.WHITE, 3, "assets/Chess_nlt45.png")
BLACK_KNIGHT = ChessPiece(Piece.KNIGHT, Color.BLACK, 3, "assets/Chess_ndt45.png")
WHITE_BISHOP = ChessPiece(Piece.BISHOP, Color.WHITE, 3, "assets/Chess_blt45.png")
BLACK_BISHOP = ChessPiece(Piece.BISHOP, Color.BLACK, 3, "assets/Chess_bdt45.png")
WHITE_QUEEN = ChessPiece(Piece.QUEEN, Color.WHITE, 10, "assets/Chess_qlt45.png")
BLACK_QUEEN = ChessPiece(Piece.QUEEN, Color.BLACK, 10, "assets/Chess_qdt45.png")
WHITE_KING = ChessPiece(Piece.KING, Color.WHITE, None, "assets/Chess_klt45.png")
BLACK_KING = ChessPiece(Piece.KING, Color.BLACK, None, "assets/Chess_kdt45.png")


class ChessEngine:
    """ A collection of static methods for determining move sets and attacked squares.
    """

    @staticmethod
    def move_set(square: Tuple[int, int], board: 'Board') -> Set[Tuple[int, int]]:
        moves = set()
        piece = board[square[0]][square[1]]
        if piece is None:
            return moves
        if piece.color == Color.WHITE:
            moves.update(ChessEngine.white_switcher[piece.piece](square, board))
        else:
            moves.update(ChessEngine.black_switcher[piece.piece](square, board))
        return moves

    @staticmethod
    def __pawn_move_set(square: Tuple[int, int], board: 'Board', color: Color) -> Set[Tuple[int, int]]:
        moves = set()
        if color == Color.WHITE and square[0] + 1 in RANKS:
            if board[square[0] + 1][square[1]] is None:
                #  White one push
                moves.add((square[0] + 1, square[1]))
                if square[0] + 2 in RANKS and square[0] == 1 and board[square[0] + 2][square[1]] is None:
                    #  White two push
                    moves.add((square[0] + 2, square[1]))
            if square[1] + 1 in FILES:
                other = board[square[0] + 1][square[1] + 1]
                if other is not None and other.color == Color.BLACK or (
                        ChessEngine.__is_enpassant(square, (square[0] + 1, square[1] + 1), board, Color.WHITE)):
                    #  White capture forward right (standard or enpassant)
                    moves.add((square[0] + 1, square[1] + 1))
            if square[1] - 1 in FILES:
                other = board[square[0] + 1][square[1] - 1]
                if other is not None and other.color == Color.BLACK or (
                        ChessEngine.__is_enpassant(square, (square[0] + 1, square[1] - 1), board, color.WHITE)):
                    #  White capture forward left (standard or enpassant)
                    moves.add((square[0] + 1, square[1] - 1))
        elif color == Color.BLACK and square[0] - 1 in RANKS:
            if board[square[0] - 1][square[1]] is None:
                #  Black one push
                moves.add((square[0] - 1, square[1]))
                if square[0] - 2 in RANKS and square[0] == 1 and board[square[0] - 2][square[1]] is None:
                    #  Black two push
                    moves.add((square[0] - 2, square[1]))
            if square[1] + 1 in FILES:
                other = board[square[0] - 1][square[1] + 1]
                if other is not None and other.color == Color.WHITE or (
                        ChessEngine.__is_enpassant(square, (square[0] - 1, square[1] + 1), board, color.BLACK)):
                    #  Black capture backward right (standard or enpassant)
                    moves.add((square[0] - 1, square[1] + 1))
            if square[1] - 1 in FILES:
                print("here")
                other = board[square[0] - 1][square[1] - 1]
                if other is not None and other.color == Color.WHITE or (
                        ChessEngine.__is_enpassant(square, (square[0] - 1, square[1] - 1), board, color.BLACK)):
                    #  White backward left (standard or enpassant)
                    moves.add((square[0] - 1, square[1] - 1))
        return moves

    @staticmethod
    def __white_pawn_move_set(square: Tuple[int, int], board: 'Board') -> Set[Tuple[int, int]]:
        return ChessEngine.__pawn_move_set(square, board, Color.WHITE)

    @staticmethod
    def __black_pawn_move_set(square: Tuple[int, int], board: 'Board') -> Set[Tuple[int, int]]:
        return ChessEngine.__pawn_move_set(square, board, Color.BLACK)

    @staticmethod
    def __rook_move_set(square: Tuple[int, int], board: 'Board') -> Set[Tuple[int, int]]:
        moves = set()
        for square[1] in RANKS:
            moves.add((square[1], square[1]))
        for square[0] in FILES:
            moves.add((square[0], square[0]))
        moves.remove(square)
        return moves

    @staticmethod
    def __knight_move_set(square: Tuple[int, int], board: 'Board') -> Set[Tuple[int, int]]:
        moves = set()
        moves.add((square[0] + 2, square[1] + 1))
        moves.add((square[0] + 2, square[1] - 1))
        moves.add((square[0] + 1, square[1] + 2))
        moves.add((square[0] + 1, square[1] - 2))
        moves.add((square[0] - 2, square[1] + 1))
        moves.add((square[0] - 2, square[1] - 1))
        moves.add((square[0] - 1, square[1] + 2))
        moves.add((square[0] - 1, square[1] - 2))
        filter(lambda i: i in INDICES, moves)
        return moves

    @staticmethod
    def __bishop_move_set(square: Tuple[int, int], board: 'Board') -> Set[Tuple[int, int]]:
        moves = set()
        for i in range(len(FILES)):
            moves.add((square[0] - i, square[1] - i))
            moves.add((square[0] + i, square[1] + i))
            moves.add((square[0] + i, square[1] - i))
            moves.add((square[0] - i, square[1] + i))
        moves.remove(square)
        filter(lambda j: j in INDICES, moves)
        return moves

    @staticmethod
    def __queen_move_set(square: Tuple[int, int], board: 'Board') -> Set[Tuple[int, int]]:
        moves = set()
        moves.update(ChessEngine.__rook_move_set(square))
        moves.update(ChessEngine.__bishop_move_set(square))
        return moves

    @staticmethod
    def __king_move_set(square: Tuple[int, int], board: 'Board') -> Set[Tuple[int, int]]:
        moves = set()
        moves.add((square[0] - 1, square[1] - 1))
        moves.add((square[0] - 1, square[1]))
        moves.add((square[0] - 1, square[1] + 1))
        moves.add((square[0], square[1] + 1))
        moves.add((square[0] + 1, square[1] + 1))
        moves.add((square[0] + 1, square[1]))
        moves.add((square[0] + 1, square[1] - 1))
        moves.add((square[0], square[1] - 1))
        moves.add((square[0], square[1] - 2))
        moves.add((square[0], square[1] + 2))
        filter(lambda i: i in INDICES, moves)
        return moves

    white_switcher = {Piece.PAWN: getattr(__white_pawn_move_set, "__func__"),
                      Piece.ROOK: getattr(__rook_move_set, "__func__"),
                      Piece.KNIGHT: getattr(__knight_move_set, "__func__"),
                      Piece.BISHOP: getattr(__bishop_move_set, "__func__"),
                      Piece.QUEEN: getattr(__queen_move_set, "__func__"),
                      Piece.KING: getattr(__king_move_set, "__func__")}
    black_switcher = copy(white_switcher)
    black_switcher[Piece.PAWN] = getattr(__black_pawn_move_set, "__func__")

    @staticmethod
    def __is_attacking(square: Tuple[int, int], board: 'Board', color: Color):
        if board[square[0]][square[1]].piece is None:
            return False
        switcher = ChessEngine.white_switcher if color.WHITE else ChessEngine.black_switcher
        for i, row in enumerate(board):
            for j, piece in enumerate(row):
                if piece is not None and piece.color == color and square in switcher[piece]((i, j)):
                    return True
        return False

    @staticmethod
    def is_white_attacking(square: Tuple[int, int], board: 'Board') -> bool:
        return ChessEngine.__is_attacking(square, board, Color.WHITE)

    @staticmethod
    def is_black_attacking(square: Tuple[int, int], board: 'Board'):
        return ChessEngine.__is_attacking(square, board, Color.BLACK)

    @staticmethod
    def __is_enpassant(start: Tuple[int, int], end: Tuple[int, int], board: 'Board', color: Color):
        if len(board.ledger) == 0:
            return False
        last_move = board.ledger[len(board.ledger) - 1]
        if last_move.piece.piece != Piece.PAWN or last_move.piece.color == color:
            return False
        if start[0] == last_move.end[0] and end[1] == last_move.end[1]:
            if color == Color.WHITE and end[0] - last_move.end[0] == 1:
                return True
            elif color == Color.BLACK and end[0] - last_move.end[0] == -1:
                return True
        return False

    #  TODO: YEET
    @staticmethod
    def __is_promotion(start: Tuple[int, int], end: Tuple[int, int], board: 'Board', color: Color) -> bool:
        piece = board[start[0]][start[1]]
        if piece is None or piece.piece != Piece.PAWN:
            return False
        if piece.color == Color.WHITE:
            if start[0] != 6 or end[0] != 7:
                return False

    @staticmethod
    def __is_white_promotion(start: Tuple[int, int], end: Tuple[int, int], board: 'Board') -> bool:
        return ChessEngine.__is_promotion(start, end, board, Color.WHITE)

    @staticmethod
    def __is_black_promotion(start: Tuple[int, int], end: Tuple[int, int], board: 'Board') -> bool:
        return ChessEngine.__is_promotion(start, end, board, Color.WHITE)


class Move:
    def __init__(self, piece: ChessPiece, start: Tuple[int, int], end: Tuple[int, int],
                 castle: bool, promotion: bool, capture: bool, enpassant: bool):
        self.__piece = piece
        self.__start = start
        self.__end = end
        self.__castle = castle
        self.__promotion = promotion
        self.__capture = capture
        self.__enpassant = enpassant

    @property
    def piece(self):
        return self.__piece

    @property
    def start(self):
        return self.__start

    @property
    def end(self):
        return self.__end

    @property
    def castle(self):
        return self.__castle

    @property
    def promotion(self):
        return self.__promotion

    @property
    def capture(self):
        return self.__capture

    @property
    def enpassant(self):
        return self.__enpassant


class Ledger:
    def __init__(self):
        self.__ledger: List[Move] = list()

    def __len__(self):
        return len(self.__ledger)

    def __getitem__(self, item: int):
        return self.__ledger[item]

    def add_move(self, move: Move) -> 'Ledger':
        self.__ledger.append(move)
        return self


class Board:
    def __init__(self):
        self.__turn: Color = Color.WHITE
        self.__board: List[List[Optional[ChessPiece]]] = [[None] * 8 for _ in range(0, 8)]
        self.__ledger: Ledger = Ledger()
        for i, col in enumerate(self.__board):
            self.__board[1][i] = WHITE_PAWN
            self.__board[6][i] = BLACK_PAWN
        self.__board[0][0] = WHITE_ROOK
        self.__board[7][0] = BLACK_ROOK
        self.__board[0][1] = WHITE_KNIGHT
        self.__board[7][1] = BLACK_KNIGHT
        self.__board[0][2] = WHITE_BISHOP
        self.__board[7][2] = BLACK_BISHOP
        self.__board[0][3] = WHITE_QUEEN
        self.__board[7][3] = BLACK_QUEEN
        self.__board[0][4] = WHITE_KING
        self.__board[7][4] = BLACK_KING
        self.__board[0][5] = WHITE_BISHOP
        self.__board[7][5] = BLACK_BISHOP
        self.__board[0][6] = WHITE_KNIGHT
        self.__board[7][6] = BLACK_KNIGHT
        self.__board[0][7] = WHITE_ROOK
        self.__board[7][7] = BLACK_ROOK

    @property
    def turn(self):
        return self.__turn

    @property
    def board(self):
        return self.__board

    @property
    def ledger(self):
        return self.__ledger

    def __getitem__(self, item: int):
        return self.__board[item]

    def __iter__(self):
        yield from self.__board


if __name__ == "__main__":
    b = Board()
    print(ChessEngine.move_set((0, 0), b))
