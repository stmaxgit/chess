from collections import namedtuple
from enum import Enum
from typing import List, Set, Tuple, Optional

import re

_RANKS: List[int] = [_ for _ in range(0, 8)]
_FILES: List[int] = _RANKS
_INDICES: Set[Tuple[int, int]] = set()
for _ in _RANKS:
    for __ in _FILES:
        _INDICES.add((_, __))


class Piece(Enum):
    PAWN = ""
    ROOK = "R"
    KNIGHT = "N"
    BISHOP = "B"
    QUEEN = "Q"
    KING = "K"


class Color(Enum):
    LIGHT = "l"
    DARK = "d"


ChessPiece = namedtuple("_ChessPiece", ["piece", "color", "value", "image"])
WHITE_PAWN = ChessPiece(Piece.PAWN, Color.LIGHT, 1, "assets/Chess_plt45.png")
BLACK_PAWN = ChessPiece(Piece.PAWN, Color.DARK, 1, "assets/Chess_pdt45.png")
WHITE_ROOK = ChessPiece(Piece.ROOK, Color.LIGHT, 5, "assets/Chess_rlt45.png")
BLACK_ROOK = ChessPiece(Piece.ROOK, Color.DARK, 5, "assets/Chess_rdt45.png")
WHITE_KNIGHT = ChessPiece(Piece.KNIGHT, Color.LIGHT, 3, "assets/Chess_nlt45.png")
BLACK_KNIGHT = ChessPiece(Piece.KNIGHT, Color.DARK, 3, "assets/Chess_ndt45.png")
WHITE_BISHOP = ChessPiece(Piece.BISHOP, Color.LIGHT, 3, "assets/Chess_blt45.png")
BLACK_BISHOP = ChessPiece(Piece.BISHOP, Color.DARK, 3, "assets/Chess_bdt45.png")
WHITE_QUEEN = ChessPiece(Piece.QUEEN, Color.LIGHT, 10, "assets/Chess_qlt45.png")
BLACK_QUEEN = ChessPiece(Piece.QUEEN, Color.DARK, 10, "assets/Chess_qdt45.png")
WHITE_KING = ChessPiece(Piece.KING, Color.LIGHT, None, "assets/Chess_klt45.png")
BLACK_KING = ChessPiece(Piece.KING, Color.DARK, None, "assets/Chess_kdt45.png")


def to_indices(algebraic_notation: str) -> Tuple[int, int]:
    """Convert a square given in algebraic chess notation to indices.
    'a4' -> (3, 0).
    """
    return int(algebraic_notation[1]) - 1, ord(algebraic_notation[0]) - ord("a")


def from_indices(indices: Tuple[int, int]) -> str:
    """Convert indices to algebraic chess notation.
    (0, 3) -> 'd1'.
    """
    return chr(indices[1] + ord("a")) + str(indices[0] + 1)


def move_set(square: str, board: "Board") -> Set[Tuple[int, int]]:
    """Get all available moves for square on board."""
    moves = set()
    square = to_indices(square)
    piece = board[square[0]][square[1]]
    if piece is None:
        return moves

    color = piece.color
    enemy_color = Color.DARK if color == Color.LIGHT else Color.LIGHT

    moves.update(_piece_dispatch_table[piece.piece](square, board, color))

    def __not_threatens_king(start: Tuple[int, int], end: Tuple[int, int]) -> bool:
        if piece == WHITE_KING:
            board.white_king_square = end
        elif piece == BLACK_KING:
            board.black_king_square = end

        board[start[0]][start[1]] = None
        captured = board[end[0]][end[1]]
        board[end[0]][end[1]] = piece

        is_threat = _is_attacking(
            board.white_king_square
            if color == Color.LIGHT
            else board.black_king_square,
            board,
            enemy_color,
        )

        board[start[0]][start[1]] = piece
        board[end[0]][end[1]] = captured

        if piece == WHITE_KING:
            board.white_king_square = square
        elif piece == BLACK_KING:
            board.black_king_square = square

        return not is_threat

    return set(filter(lambda m: (__not_threatens_king(square, m)), moves))


def read_pgn_to_board(file_path: str) -> "Board":
    """Build a board from a game recorded in pgn format."""
    with open(file_path) as f:
        while f.readline() is not "\n":
            pass
        moves = re.findall(r"([A-Za-z]\w+|O-O-O|O-O)", f.read())

        def __process_move(s: str, color: Color, board: "Board") -> None:
            #  Handle castling cases
            if s == "O-O":
                if color == Color.LIGHT:
                    board.move("e1", "g1")
                else:
                    board.move("e8", "g8")
                return
            elif s == "O-O-O":
                if color == Color.LIGHT:
                    board.move("e1", "c1")
                else:
                    board.move("e8", "c8")
                return

            #  Remove capture, check, checkmate data
            trimmed = s.replace("x", "").replace("+", "").replace("#", "")

            if "R" in trimmed:
                piece = WHITE_ROOK if color == color.LIGHT else BLACK_ROOK
            elif "N" in trimmed:
                piece = WHITE_KNIGHT if color == color.LIGHT else BLACK_KNIGHT
            elif "B" in trimmed:
                piece = WHITE_BISHOP if color == color.LIGHT else BLACK_BISHOP
            elif "Q" in trimmed:
                piece = WHITE_QUEEN if color == color.LIGHT else BLACK_QUEEN
            elif "K" in trimmed:
                piece = WHITE_KING if color == color.LIGHT else BLACK_KING
            else:
                piece = WHITE_PAWN if color == color.LIGHT else BLACK_PAWN
                if "=" in s:
                    trimmed = trimmed[0:len(trimmed) - 2]

            #  Can directly read end square, it is not ambiguous
            end = trimmed[len(trimmed) - 2:len(trimmed)]

            #  Start square needs more processing due to possible ambiguity; e.g.,
            #  multiple of the same piece can move to the end square.
            valid_squares = set()
            for i, row in enumerate(board):
                for j, other in enumerate(row):
                    if other == piece:
                        square = from_indices((i, j))
                        if to_indices(end) in move_set(square, board):
                            valid_squares.add(square)

            #  If only one of this piece can move to end, it must be that piece.
            if len(valid_squares) == 1:
                start = valid_squares.pop()
                board.move(start, end)
                return

            #  Otherwise, there should be (at least) a file in the passed string.
            file = ord(trimmed[1]) - ord("a")
            valid_squares = set()
            for i, row in enumerate(board):
                other = row[file]
                if other == piece:
                    square = from_indices((i, file))
                    if to_indices(end) in move_set(square, board):
                        valid_squares.add(square)
            if len(valid_squares) == 1:
                start = valid_squares.pop()

            # Still ambiguous; there must be a rank in the passed string.
            else:
                start = trimmed[1:3]

            game.move(start, end)

        game = Board()
        for idx, move in enumerate(moves):
            __process_move(move, Color.LIGHT if idx % 2 == 0 else Color.DARK, game)
        return game


def _pawn_move_set(
    square: Tuple[int, int], board: "Board", color: Color
) -> Set[Tuple[int, int]]:
    moves = set()
    if color == Color.LIGHT and square[0] + 1 in _RANKS:
        if board[square[0] + 1][square[1]] is None:
            #  White one push
            moves.add((square[0] + 1, square[1]))
            if (
                square[0] + 2 in _RANKS
                and square[0] == 1
                and board[square[0] + 2][square[1]] is None
            ):
                #  White two push
                moves.add((square[0] + 2, square[1]))
        if square[1] + 1 in _FILES:
            other = board[square[0] + 1][square[1] + 1]
            if (
                other is not None
                and other.color == Color.DARK
                or (_is_enpassant(square, (square[0] + 1, square[1] + 1), board))
            ):
                #  White capture forward right (standard or enpassant)
                moves.add((square[0] + 1, square[1] + 1))
        if square[1] - 1 in _FILES:
            other = board[square[0] + 1][square[1] - 1]
            if (
                other is not None
                and other.color == Color.DARK
                or (_is_enpassant(square, (square[0] + 1, square[1] - 1), board))
            ):
                #  White capture forward left (standard or enpassant)
                moves.add((square[0] + 1, square[1] - 1))
    elif color == Color.DARK and square[0] - 1 in _RANKS:
        if board[square[0] - 1][square[1]] is None:
            #  Black one push
            moves.add((square[0] - 1, square[1]))
            if (
                square[0] - 2 in _RANKS
                and square[0] == 6
                and board[square[0] - 2][square[1]] is None
            ):
                #  Black two push
                moves.add((square[0] - 2, square[1]))
        if square[1] + 1 in _FILES:
            other = board[square[0] - 1][square[1] + 1]
            if (
                other is not None
                and other.color == Color.LIGHT
                or (_is_enpassant(square, (square[0] - 1, square[1] + 1), board))
            ):
                #  Black capture backward right (standard or enpassant)
                moves.add((square[0] - 1, square[1] + 1))
        if square[1] - 1 in _FILES:
            other = board[square[0] - 1][square[1] - 1]
            if (
                other is not None
                and other.color == Color.LIGHT
                or (_is_enpassant(square, (square[0] - 1, square[1] - 1), board))
            ):
                #  White backward left (standard or enpassant)
                moves.add((square[0] - 1, square[1] - 1))
    return moves


def _rook_move_set(
    square: Tuple[int, int], board: "Board", color: Color
) -> Set[Tuple[int, int]]:
    moves = set()

    #  Check above along current file
    curr_rank = square[0] + 1
    while curr_rank <= 7:
        if board[curr_rank][square[1]] is None:
            moves.add((curr_rank, square[1]))
        else:
            if board[curr_rank][square[1]].color != color:
                moves.add((curr_rank, square[1]))
                break
            else:
                break
        curr_rank += 1

    #  Check below along current file
    curr_rank = square[0] - 1
    while curr_rank >= 0:
        if board[curr_rank][square[1]] is None:
            moves.add((curr_rank, square[1]))
        else:
            if board[curr_rank][square[1]].color != color:
                moves.add((curr_rank, square[1]))
                break
            else:
                break
        curr_rank -= 1

    #  Check right along current rank
    curr_file = square[1] + 1
    while curr_file <= 7:
        if board[square[0]][curr_file] is None:
            moves.add((square[0], curr_file))
        else:
            if board[square[0]][curr_file].color != color:
                moves.add((square[0], curr_file))
                break
            else:
                break
        curr_file += 1

    #  Check left along current rank
    curr_file = square[1] - 1
    while curr_file >= 0:
        if board[square[0]][curr_file] is None:
            moves.add((square[0], curr_file))
        else:
            if board[square[0]][curr_file].color != color:
                moves.add((square[0], curr_file))
                break
            else:
                break
        curr_file -= 1

    return moves


def _knight_move_set(
    square: Tuple[int, int], board: "Board", color: Color
) -> Set[Tuple[int, int]]:
    moves = set()
    moves.add((square[0] + 2, square[1] + 1))
    moves.add((square[0] + 2, square[1] - 1))
    moves.add((square[0] + 1, square[1] + 2))
    moves.add((square[0] + 1, square[1] - 2))
    moves.add((square[0] - 2, square[1] + 1))
    moves.add((square[0] - 2, square[1] - 1))
    moves.add((square[0] - 1, square[1] + 2))
    moves.add((square[0] - 1, square[1] - 2))
    moves = filter(lambda i: i in _INDICES, moves)

    return set(filter(lambda m: _is_not_occupied_by_same_color(m, board, color), moves))


def _bishop_move_set(
    square: Tuple[int, int], board: "Board", color: Color
) -> Set[Tuple[int, int]]:
    moves = set()

    #  Check up-left
    curr_rank = square[0] + 1
    curr_file = square[1] - 1
    while curr_rank <= 7 and curr_file >= 0:
        if board[curr_rank][curr_file] is None:
            moves.add((curr_rank, curr_file))
        else:
            if board[curr_rank][curr_file].color != color:
                moves.add((curr_rank, curr_file))
                break
            else:
                break
        curr_rank += 1
        curr_file -= 1

    #  Check down-left
    curr_rank = square[0] - 1
    curr_file = square[1] - 1
    while curr_rank >= 0 and curr_file >= 0:
        if board[curr_rank][curr_file] is None:
            moves.add((curr_rank, curr_file))
        else:
            if board[curr_rank][curr_file].color != color:
                moves.add((curr_rank, curr_file))
                break
            else:
                break
        curr_rank -= 1
        curr_file -= 1

    #  Check up-right
    curr_rank = square[0] + 1
    curr_file = square[1] + 1
    while curr_rank <= 7 and curr_file <= 7:
        if board[curr_rank][curr_file] is None:
            moves.add((curr_rank, curr_file))
        else:
            if board[curr_rank][curr_file].color != color:
                moves.add((curr_rank, curr_file))
                break
            else:
                break
        curr_rank += 1
        curr_file += 1

    #  Check down-right
    curr_rank = square[0] - 1
    curr_file = square[1] + 1
    while curr_rank >= 0 and curr_file <= 7:
        if board[curr_rank][curr_file] is None:
            moves.add((curr_rank, curr_file))
        else:
            if board[curr_rank][curr_file].color != color:
                moves.add((curr_rank, curr_file))
                break
            else:
                break
        curr_rank -= 1
        curr_file += 1

    return moves


def _queen_move_set(
    square: Tuple[int, int], board: "Board", color: Color
) -> Set[Tuple[int, int]]:
    moves = set()
    moves.update(_rook_move_set(square, board, color))
    moves.update(_bishop_move_set(square, board, color))
    return moves


def _king_move_set(
    square: Tuple[int, int], board: "Board", color: Color
) -> Set[Tuple[int, int]]:
    def __can_castle(a_file: bool, m: Set[Tuple[int, int]]) -> bool:
        if color == color.LIGHT:
            if board.ledger.has_white_king_moved:
                return False
            if a_file:
                if board.ledger.has_white_a_rook_moved:
                    return False
                if (
                    board[0][1] is not None
                    or board[0][2] is not None
                    or board[0][3] is not None
                ):
                    return False
                for sq in {(0, 0), (0, 1), (0, 2), (0, 3), (0, 4)}:
                    if _is_attacking(sq, board, color.DARK):
                        return False
                m.add((0, 2))
                return True
            else:
                if board.ledger.has_white_h_rook_moved:
                    return False
                if board[0][5] is not None or board[0][6] is not None:
                    return False
                for sq in {(0, 4), (0, 5), (0, 6), (0, 7)}:
                    if _is_attacking(sq, board, color.DARK):
                        return False
                m.add((0, 6))
                return True
        else:
            if board.ledger.has_black_king_moved:
                return False
            if a_file:
                if board.ledger.has_black_a_rook_moved:
                    return False
                if (
                    board[7][1] is not None
                    or board[7][2] is not None
                    or board[7][3] is not None
                ):
                    return False
                for sq in {(7, 0), (7, 1), (7, 2), (7, 3), (7, 4)}:
                    if _is_attacking(sq, board, color.LIGHT):
                        return False
                m.add((7, 2))
                return True
            else:
                if board.ledger.has_black_h_rook_moved:
                    return False
                if board[7][5] is not None or board[7][6] is not None:
                    return False
                for sq in {(7, 4), (7, 5), (7, 6), (7, 7)}:
                    if _is_attacking(sq, board, color.LIGHT):
                        return False
                    m.add((7, 6))
                    return True

    moves = set()
    moves.add((square[0] - 1, square[1] - 1))
    moves.add((square[0] - 1, square[1]))
    moves.add((square[0] - 1, square[1] + 1))
    moves.add((square[0], square[1] + 1))
    moves.add((square[0] + 1, square[1] + 1))
    moves.add((square[0] + 1, square[1]))
    moves.add((square[0] + 1, square[1] - 1))
    moves.add((square[0], square[1] - 1))

    moves = set(filter(lambda i: i in _INDICES, moves))

    moves = set(
        filter(lambda m: _is_not_occupied_by_same_color(m, board, color), moves)
    )

    if board.turn == color:
        __can_castle(True, moves)
        __can_castle(False, moves)

    return moves


_piece_dispatch_table = {
    Piece.PAWN: _pawn_move_set,
    Piece.ROOK: _rook_move_set,
    Piece.KNIGHT: _knight_move_set,
    Piece.BISHOP: _bishop_move_set,
    Piece.QUEEN: _queen_move_set,
    Piece.KING: _king_move_set,
}


def _is_not_occupied_by_same_color(
    square: Tuple[int, int], board: "Board", color: Color
) -> bool:
    if board[square[0]][square[1]] is None:
        return True
    if board[square[0]][square[1]].color == color:
        return False
    return True


def _is_attacking(square: Optional[Tuple[int, int]], board: "Board", color: Color):
    for rank in _RANKS:
        for file in _FILES:
            piece = board[rank][file]
            if (
                piece is not None
                and piece.color == color
                and (
                    square
                    in _piece_dispatch_table[piece.piece](
                        (rank, file), board, piece.color
                    )
                )
            ):
                return True
    return False


def _is_enpassant(start: Tuple[int, int], end: Tuple[int, int], board: "Board"):
    piece = board[start[0]][start[1]]
    if (
        piece is None
        or (piece != WHITE_PAWN and piece != BLACK_PAWN)
        or len(board.ledger) == 0
    ):
        return False
    last_move = board.ledger[len(board.ledger) - 1]
    if last_move.piece.piece != Piece.PAWN:
        return False
    if start[0] == last_move.end[0] and end[1] == last_move.end[1]:
        if piece.color == Color.LIGHT and end[0] - last_move.end[0] == 1:
            return True
        elif piece.color == Color.DARK and end[0] - last_move.end[0] == -1:
            return True
    return False


def _is_promotion(start: Tuple[int, int], end: Tuple[int, int], board: "Board") -> bool:
    piece = board[start[0]][start[1]]
    if piece is None or piece.piece != Piece.PAWN:
        return False
    if piece.color == Color.LIGHT:
        if start[0] != 6 or end[0] != 7:
            return False
    elif piece.color == Color.DARK:
        if start[0] != 1 or end[0] != 0:
            return False
    return True


def _is_castle(start: Tuple[int, int], end: Tuple[int, int], board: "Board") -> bool:
    if (
        board[start[0]][start[1]] != WHITE_KING
        and board[start[0]][start[1]] != BLACK_KING
    ):
        return False
    return abs(start[1] - end[1]) == 2


class _Move:
    def __init__(
        self,
        piece: ChessPiece,
        start: Tuple[int, int],
        end: Tuple[int, int],
        castle: bool = False,
        promotion: bool = False,
        capture: bool = False,
        enpassant: bool = False,
        check: bool = False,
        checkmate: bool = False,
    ):
        self.__piece = piece
        self.__start = start
        self.__end = end
        self.__castle = castle
        self.__promotion = promotion
        self.__capture = capture
        self.__enpassant = enpassant
        self.__check = check
        self.__checkmate = checkmate

    #  TODO: conform to pgn standard
    def __repr__(self):
        if self.__castle:
            if self.__end[1] == 0:
                return "O-O-O"
            else:
                return "O-O"
        return (
            self.__piece.piece.value
            + ("x" if self.__capture else "")
            + from_indices(self.__end)
        )

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

    @property
    def check(self):
        return self.__check

    @property
    def checkmate(self):
        return self.__checkmate


class Ledger:
    def __init__(self):
        self.__ledger: List[_Move] = list()
        self.__str_format: str = ""
        self.__has_white_king_moved: bool = False
        self.__has_black_king_moved: bool = False
        self.__has_white_a_rook_moved: bool = False
        self.__has_black_a_rook_moved: bool = False
        self.__has_white_h_rook_moved: bool = False
        self.__has_black_h_rook_moved: bool = False

    def __len__(self):
        return len(self.__ledger)

    def __getitem__(self, item: int):
        return self.__ledger[item]

    def __repr__(self):
        return self.__str_format

    @property
    def has_white_king_moved(self):
        return self.__has_white_king_moved

    @property
    def has_black_king_moved(self):
        return self.__has_black_king_moved

    @property
    def has_white_a_rook_moved(self):
        return self.__has_white_a_rook_moved

    @property
    def has_black_a_rook_moved(self):
        return self.__has_black_a_rook_moved

    @property
    def has_white_h_rook_moved(self):
        return self.__has_white_h_rook_moved

    @property
    def has_black_h_rook_moved(self):
        return self.__has_black_h_rook_moved

    def add_move(self, move: _Move) -> "Ledger":
        if move.piece == WHITE_KING:
            self.__has_white_king_moved = True
        elif move.piece == BLACK_KING:
            self.__has_black_king_moved = True
        elif move.piece == WHITE_ROOK:
            if move.start == (0, 0):
                self.__has_white_a_rook_moved = True
            elif move.start == (0, 7):
                self.__has_white_h_rook_moved = True
        elif move.piece == BLACK_ROOK:
            if move.start == (7, 0):
                self.__has_black_a_rook_moved = True
            elif move.start == (7, 7):
                self.__has_black_h_rook_moved = True
        self.__ledger.append(move)
        self.__str_format += (
            str(len(self.__ledger) // 2 + 1) + "." + move.__repr__()
            if len(self.__ledger) % 2 != 0
            else " " + move.__repr__() + " "
        )
        return self


class Board:
    def __init__(self, empty: bool = False, turn: Color = Color.LIGHT):
        self.__turn = turn
        self.__hold_for_promotion: bool = False
        self.__board: List[List[Optional[ChessPiece]]] = [
            [None] * 8 for _ in range(0, 8)
        ]
        self.__ledger: Ledger = Ledger()
        self.__white_king_square: Optional[Tuple[int, int]] = None
        self.__black_king_square: Optional[Tuple[int, int]] = None
        if not empty:
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
            self.__white_king_square = (0, 4)
            self.__black_king_square = (7, 4)

    def __repr__(self):
        out = ""
        for rank in _RANKS[::-1]:
            out += str(rank + 1) + " | "
            for file in _FILES:
                out += (
                    " - "
                    if self.__board[rank][file] is None
                    else self.__board[rank][file].color.value
                    + self.__board[rank][file].piece.value
                    + " "
                )
            out += "|\n"
        out += "   "
        for rank in _RANKS:
            out += "  " + chr(ord("a") + rank)

        return out

    @property
    def turn(self) -> Color:
        return self.__turn

    @property
    def ledger(self) -> Ledger:
        return self.__ledger

    @property
    def white_king_square(self) -> Optional[Tuple[int, int]]:
        return self.__white_king_square

    @white_king_square.setter
    def white_king_square(self, value: Tuple[int, int]):
        self.__white_king_square = value

    @property
    def black_king_square(self) -> Optional[Tuple[int, int]]:
        return self.__black_king_square

    @black_king_square.setter
    def black_king_square(self, value: Tuple[int, int]):
        self.__black_king_square = value

    def attach(self, square: str, piece: ChessPiece) -> "Board":
        square = to_indices(square)
        self.__board[square[0]][square[1]] = piece
        if piece == WHITE_KING:
            self.__white_king_square = square
        elif piece == BLACK_KING:
            self.__black_king_square = square
        return self

    def __getitem__(self, item: int):
        return self.__board[item]

    def __iter__(self):
        yield from self.__board

    def move(self, start: str, end: str) -> bool:
        if self.__hold_for_promotion:
            return False
        if to_indices(end) not in move_set(start, self):
            return False

        start, end = to_indices(start), to_indices(end)
        piece = self.__board[start[0]][start[1]]
        self.__ledger.add_move(
            _Move(
                piece=piece,
                start=start,
                end=end,
                castle=_is_castle(start, end, self),
                promotion=_is_promotion(start, end, self),
                capture=True if self.__board[end[0]][end[1]] is not None else False,
                enpassant=_is_enpassant(start, end, self),
            )
        )
        self.__board[start[0]][start[1]] = None
        self.__board[end[0]][end[1]] = piece
        last_move = self.__ledger[len(self.__ledger) - 1]

        if piece == WHITE_KING:
            self.__white_king_square = end
            if last_move.castle:
                if end[1] == 2:
                    self.__board[0][0] = None
                    self.__board[0][3] = WHITE_ROOK
                else:
                    self.__board[0][7] = None
                    self.__board[0][5] = WHITE_ROOK
        elif piece == BLACK_KING:
            self.__black_king_square = end
            if last_move.castle:
                if end[1] == 2:
                    self.__board[7][0] = None
                    self.__board[7][3] = BLACK_ROOK
                else:
                    self.__board[7][7] = None
                    self.__board[7][5] = BLACK_ROOK
        if last_move.enpassant:
            self.__board[last_move.end[0]][last_move.end[1]] = None
        elif last_move.promotion:
            self.__hold_for_promotion = True

        self.__turn = Color.LIGHT if self.__turn != Color.LIGHT else Color.DARK
        return True


if __name__ == "__main__":
    import cProfile

    cProfile.run(
        'read_pgn_to_board("test/games/ct-2863-2675-2020.4.7.pgn")', sort="time"
    )
    t = read_pgn_to_board("test/games/ct-2863-2675-2020.4.7.pgn")
