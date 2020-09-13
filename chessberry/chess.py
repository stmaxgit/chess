import abc
from typing import List, Tuple, Set
from math import copysign
from copy import deepcopy

from chessberry.constants import *


def to_indices(algebraic_notation: str) -> Tuple[int, int]:
    """Indices go file in [0, 7], rank in [0, 7]."""
    return ord(algebraic_notation[0]) - ord('a'), int(algebraic_notation[1]) - 1


def from_indices(indices: Tuple[int, int]) -> str:
    return chr(indices[0] + ord('a')) + str(indices[1] + 1)


class Piece(abc.ABC):
    """Abstract class for a chess piece.

    :param algebraic_notation: Algebraic notation of square the piece occupies.
    :param color: Color of piece.
    """

    IMAGE_WHITE, IMAGE_BLACK = None, None

    def __init__(self, algebraic_notation: str, color: bool):
        self.square = algebraic_notation
        self.indices = to_indices(algebraic_notation)
        self.color = color

    @property
    def image(self):
        return self.IMAGE_WHITE if self.color == WHITE else self.IMAGE_BLACK

    @property
    @abc.abstractmethod
    def value(self) -> int:
        """Piece specific value."""

    @property
    def file(self) -> int:
        return self.indices[0]

    @property
    def rank(self) -> int:
        return self.indices[1]

    @abc.abstractmethod
    def get_moves_no_board(self) -> Set[Tuple[int, int]]:
        """Implement piece specific movement logic here without considering board state; e.g. pin on King, etc. """

    @abc.abstractmethod
    def can_move_to_no_self_check_test(self, end: str, game: 'Game') -> bool:
        """Determine whether this piece can move to a square given board state without testing for a self check."""

    def update(self, algebraic_notation: str, color: bool):
        self.square = algebraic_notation
        self.color = color


class Move:
    """A container class for a game move.

    :param game: A reference to the current game.
    :param piece: A reference to the current piece.
    :param start: Algebraic notation of initial square.
    :param end: Algebraic notation of final square.
    """
    def __init__(self, game: 'Game', piece: Piece, start: str, end: str):
        self.game = game
        #  Do not want aliasing, want a snapshot of game state at this time.
        self.piece = deepcopy(piece)
        #  Keeping an alias for this piece is useful for the gui programming.
        self.piece_alias = piece
        self.start = start
        self.to = end


class Capture(Move):
    """A container class for a game capture. Contains more information (the captured piece) than just a move.

    :param game: A reference to the current game.
    :param attacker: A reference to the current piece.
    :param start: Algebraic notation of initial square.
    :param end: Algebraic notation of final square.
    :param defender: A reference to the captured piece.
    """
    def __init__(self, game: 'Game', attacker: Piece, start: str, end: str, defender: Piece):
        self.captured = deepcopy(defender)
        self.captured_alias = defender
        super().__init__(game, attacker, start, end)


class Castle(Move):
    """A container class for a game castle. Contains more information (the rook castled to) than just a move.

    :param game: A reference to the current game.
    :param king: A reference to the castling king.
    :param start: Algebraic notation of initial square.
    :param end: Algebraic notation of final square.
    :param rook: A reference to the castling rook.
    """
    def __init__(self, game: 'Game', king: 'King', start: str, end: str, rook: 'Rook'):
        self.rook = deepcopy(rook)
        self.rook_alias = rook
        super().__init__(game, king, start, end)


class MoveLedger:
    """A container class to store past moves on a game. Internally, just a list."""

    def __init__(self):
        self.__moves: List[Move] = list()

    def __getitem__(self, item: int) -> Move:
        return self.__moves[item]

    def __len__(self) -> int:
        return len(self.__moves)

    def append(self, move: Move) -> None:
        """Append internal list."""
        self.__moves.append(move)

    def last(self) -> Move or None:
        """Convenience method for end of the move ledger. Could return None if the ledger is empty."""
        if len(self.__moves) != 0:
            return self.__moves[len(self.__moves) - 1]


class Board:
    """Represents a chess board. Internally, the state is stored as a 8x8 array, where elements are either a piece
    instance or point to EMPTY. Some references are kept to key pieces so as to not search all of the state array
    to find them every time they are needed.

    :param state: Will default to an empty board if no state array is supplied. It is recommended to create an empty
    board and use the attach method to add pieces.
    """
    def __init__(self, state: List[List[Piece or EMPTY]] = None):
        super().__init__()
        self.__state = state if state is not None else [[EMPTY] * 8 for _ in range(8)]
        #  Keeping references to the kings and rooks so that we will not have to find them every move
        self.__white_king: King = EMPTY
        self.__black_king: King = EMPTY
        self.__white_rooks: List[Rook] = list()
        self.__black_rooks: List[Rook] = list()
        for piece in self:
            self.attach(piece)

    def __getitem__(self, algebraic_notation: str):
        indices = to_indices(algebraic_notation)
        return self.__state[indices[0]][indices[1]]

    def __iter__(self):
        yield from [piece for file in self.__state for piece in file if piece is not EMPTY]

    def __repr__(self):
        out = ''
        for i in range(len(self.__state)):
            out += '\n' + '  ' + str([str(elem) + ' ' * (len(str(EMPTY)) - len(str(elem))) for elem in self.__state[i]])
        out += '\n'
        return f"Board({out})"

    @property
    def state(self):
        return self.__state

    def attach(self, piece: Piece) -> bool:
        """Attach a piece to the board. Will fail is the square is already occupied."""
        if self[piece.square] != EMPTY:
            return False
        if isinstance(piece, King):
            if piece.color == WHITE:
                self.__white_king = piece
            else:
                self.__black_king = piece
        elif isinstance(piece, Rook):
            if piece.color == WHITE:
                self.__white_rooks.append(piece)
            else:
                self.__black_rooks.append(piece)
        self.__state[piece.file][piece.rank] = piece
        return True

    def detach(self, piece) -> bool:
        """Detach a piece from the board."""
        if isinstance(piece, King):
            self.__white_king = EMPTY if piece.color == WHITE else self.__white_king
            self.__black_king = EMPTY if piece.color == BLACK else self.__black_king
        elif isinstance(piece, Rook):
            if piece.color == WHITE:
                self.__white_rooks.remove(piece)
            else:
                self.__black_rooks.remove(piece)
        self.__state[piece.file][piece.rank] = EMPTY
        return True

    def get_king(self, color: bool):
        return self.__white_king if color == WHITE else self.__black_king

    def get_rooks(self, color: bool):
        return self.__white_rooks if color == WHITE else self.__black_rooks


class Game:
    """Mediator class for pieces and board.

    :param board: A reference to a board. If none is provided, a board will be populated in starting configuration.
    """

    def __init__(self, board: Board = None):
        self.whose_move: bool = WHITE
        self.move_ledger: MoveLedger = MoveLedger()
        if board is None:
            board = Board()
            board.attach(Rook('a1', WHITE))
            board.attach(Knight('b1', WHITE))
            board.attach(Bishop('c1', WHITE))
            board.attach(Queen('d1', WHITE))
            board.attach(King('e1', WHITE))
            board.attach(Bishop('f1', WHITE))
            board.attach(Knight('g1', WHITE))
            board.attach(Rook('h1', WHITE))
            for file in FILES_ALG:
                board.attach(Pawn(file + '2', WHITE))
            board.attach(Rook('a8', BLACK))
            board.attach(Knight('b8', BLACK))
            board.attach(Bishop('c8', BLACK))
            board.attach(Queen('d8', BLACK))
            board.attach(King('e8', BLACK))
            board.attach(Bishop('f8', BLACK))
            board.attach(Knight('g8', BLACK))
            board.attach(Rook('h8', BLACK))
            for file in FILES_ALG:
                board.attach(Pawn(file + '7', BLACK))
            self.board = board
        else:
            self.board = board

    def __getitem__(self, algebraic_notation: str):
        return self.board[algebraic_notation]

    def __repr__(self):
        return self.board.__repr__()

    def move(self, start: str, end: str) -> bool:
        """Move a piece from start to end. Will return True if the move is valid and perform the move. Side effects
        will be piece properties updated and board properties updated. If a move is invalid, will return False with
        no changes to piece or board.

        Checks go something like this:
        If start is empty, return False.
        If piece color is not the current player's color, return False.
        If end is not in the pieces' standard set of moves, not considering board state, return False.
        If the move is not by our king and places our king in check, return False. Else, return True.
        If the move is by our king and places our king in check, return False. Else, return True.
        If the move is our king castling and castling is invalid, return False. Else, return True.

        Internally, some tests will update piece and board state and then check if the king is threatened. These
        updates will be reverted if he is threatened.

        :param start: Algebraic notation of initial square.
        :param end: Algebraic notation of final square.
        """

        piece = self[start]
        if piece is EMPTY:
            return False
        if piece.color != self.whose_move:
            return False
        if not piece.can_move_to_no_self_check_test(end, self):
            return False

        start_file, start_rank = piece.indices[:]  # Make a copy so we can revert to this state if needed
        end_file, end_rank = to_indices(end)
        end_piece = self.board.state[end_file][end_rank]  # Hold a reference to the end piece so we can revert if needed
        #  Likewise, need to hold a reference to possible enpassant square
        enpassant_rank = end_rank - 1 if piece.color == WHITE else end_rank + 1
        if enpassant_rank in RANKS_IDX:
            captured_piece_enpassant = (
                self.board.state[end_file][end_rank - 1 if piece.color == WHITE else end_rank + 1])
        else:
            captured_piece_enpassant = EMPTY
        our_king = self.board.get_king(piece.color)

        #  Determine if move is enpassant
        is_enpassant = False
        if isinstance(piece, Pawn) and piece.is_enpassant(end, self):
            is_enpassant = True
            #  Update enpassant square, maybe temporarily
            self.board.state[end_file][captured_piece_enpassant.rank] = EMPTY

        #  Non-king movement
        if piece is not our_king:
            #  Update board and pieces, maybe temporarily
            piece.indices = end_file, end_rank
            self.board.state[start_file][start_rank] = EMPTY
            self.board.state[end_file][end_rank] = piece
            #  Pieces we should check for attacking our king
            threats = [other for other in self.board if other.color != piece.color]
            for threat in threats:
                if threat.can_move_to_no_self_check_test(our_king.square, self):
                    #  Return pieces and board to original state, cannot move
                    piece.indices = start_file, start_rank
                    self.board.state[start_file][start_rank] = piece
                    self.board.state[end_file][end_rank] = end_piece
                    #  This will be EMPTY if it is not an enpassant move; otherwise, it will be an enemy pawn.
                    self.board.state[end_file][end_rank - 1 if piece.color == WHITE else end_rank + 1] = (
                        captured_piece_enpassant)
                    return False
            piece.square = end
            if is_enpassant:
                self.move_ledger.append(Capture(self, piece, start, end, captured_piece_enpassant))
            else:
                self.move_ledger.append(Move(self, piece, start, end) if end_piece is EMPTY else
                                        Capture(self, piece, start, end, end_piece))
            self.whose_move = not self.whose_move
            return True

        #  King movement
        is_castle = False
        castles_to = None
        dx = end_file - piece.indices[0]
        direction = LEFT if dx < 0 else RIGHT
        if abs(dx) == 2:
            rooks = self.board.get_rooks(piece.color)
            for rook in rooks:
                if abs(rook.indices[0] - end_file) < abs(rook.indices[0] - piece.indices[0]):
                    is_castle = True
                    castles_to = rook
        else:
            #  Update board and pieces, maybe temporarily
            piece.indices = end_file, end_rank
            self.board.state[start_file][start_rank] = EMPTY
            self.board.state[end_file][end_rank] = piece
            #  Pieces we should check for attacking our king
            threats = [other for other in self.board if other.color != piece.color]
            for threat in threats:
                if threat.can_move_to_no_self_check_test(piece.square, self):
                    #  Return pieces and board to original state, cannot move
                    piece.indices = start_file, start_rank
                    self.board.state[start_file][start_rank] = piece
                    self.board.state[end_file][end_rank] = end_piece
                    return False
                piece.square = end
                self.move_ledger.append(Move(self, piece, start, end) if end_piece is EMPTY else
                                        Capture(self, piece, start, end, end_piece))
                self.whose_move = not self.whose_move
                return True

        if is_castle and piece.can_castle(castles_to, self):
            self.board.state[start_file][start_rank] = EMPTY
            self.board.state[castles_to.file][castles_to.rank] = EMPTY
            piece.indices = end_file, end_rank
            piece.square = end
            castles_to.indices = (piece.indices[0] + 1 if direction == LEFT else piece.indices[0] - 1,
                                  castles_to.indices[1])
            castles_to.square = from_indices(castles_to.indices)
            self.board.state[end_file][end_rank] = piece
            self.board.state[castles_to.file][castles_to.rank] = castles_to
            self.move_ledger.append(Castle(self, piece, start, end, castles_to))
            self.whose_move = not self.whose_move
            return True
        return False


class Pawn(Piece):
    """A chess pawn. Knows about pawn movement behavior.

    :param algebraic_notation: Algebraic notation of the square the piece occupies.
    :param color: Color of the piece.
    """

    VALUE = 1
    IMAGE_WHITE = 'assets/Chess_plt45.png'
    IMAGE_BLACK = 'assets/Chess_pdt45.png'

    def __init__(self, algebraic_notation: str, color: bool):
        super().__init__(algebraic_notation, color)

    def __repr__(self):
        return f"{self.square}"

    @property
    def value(self):
        return Pawn.VALUE

    @staticmethod
    def __map_ranks(rank: int) -> int:
        #  A little trick to map black ranks to white ranks (or vice-versa!)
        #  so it is not necessary to consider them separately.
        return abs(rank - 7)

    @staticmethod
    def __get_moves_no_board_check_white(indices: Tuple[int, int]) -> Set[Tuple[int, int]]:
        file, rank = indices
        moves = set()
        moves.add((file, rank + 1))
        moves.add((file, rank + 2))
        moves.add((file + 1, rank + 1))
        moves.add((file - 1, rank + 1))
        return set(filter(lambda i: i in INDICES, moves))

    def get_moves_no_board(self) -> Set[Tuple[int, int]]:
        """Get standard set of moves not considering board state. That is, moves that require a capture or specific rank
        (a two-push) are included regardless. Helpful in eliminating large sets of moves.

        :returns moves: A set of array indices tuples."""
        moves = self.__get_moves_no_board_check_white(
            self.indices if self.color == WHITE else (self.file, self.__map_ranks(self.rank)))
        if self.color == BLACK:
            black_moves = set()
            for move in moves:
                black_moves.add((move[0], self.__map_ranks(move[1])))
                moves = black_moves
        return moves

    def is_enpassant(self, end: str, game: Game) -> bool:
        new_file, new_rank = to_indices(end)
        new_rank_white = new_rank if self.color == WHITE else self.__map_ranks(new_rank)

        adjacent_files = filter(lambda i: i in FILES_IDX, {self.file + 1, self.file - 1})
        adjacent_pawns = {game.board.state[file][self.rank] for file in adjacent_files if
                          isinstance(game.board.state[file][self.rank], Pawn)}
        adjacent_pawns = set(filter(lambda i: i.color != self.color, adjacent_pawns))
        for pawn in adjacent_pawns:
            if len(game.move_ledger) != 0 and game.move_ledger.last().piece_alias is pawn:
                #  Map captured rank to black if necessary
                piece_black_rank = pawn.rank if pawn.color == BLACK else self.__map_ranks(pawn.rank)
                if (new_file, new_rank_white) == (pawn.indices[0], piece_black_rank + 1):
                    return True
        return False

    def can_move_to_no_self_check_test(self, end: str, game: Game) -> bool:
        """Check whether a move to end is valid given a game.

        :param end: Algebraic notation of final square.
        :param game: Reference to a game instance.

        :returns bool: True if move is valid, otherwise False.
        """
        new_file, new_rank = to_indices(end)
        #  Quickly cull unconditionally unavailable moves
        new_rank_white = new_rank if self.color == WHITE else self.__map_ranks(new_rank)
        curr_file = self.file
        curr_rank_white = self.rank if self.color == WHITE else self.__map_ranks(self.rank)
        if (new_file, new_rank_white) not in (
                self.__get_moves_no_board_check_white((curr_file, curr_rank_white))):
            return False

        if self.is_enpassant(end, game):
            return True

        if game[end] is EMPTY:
            #  Empty square precludes change of file (having just ruled out enpassant)
            if new_file - curr_file != 0:
                return False
            if curr_rank_white == 1:
                return True if new_rank_white in {2, 3} else False
            else:
                return True if new_rank_white - curr_rank_white == 1 else False
        else:
            #  The square must be occupied
            pawn = game[end]
            #  Cannot attack own piece
            if self.color == pawn.color:
                return False

            #  Boolean value for whether the piece is on an adjacent file, which is necessary for a capture.
            off_file = pawn.file - 1 == self.file or pawn.file + 1 == self.file

            #  Standard pawn capture, off file and captured pawn is ahead of this pawn.
            if off_file and new_rank_white - 1 == curr_rank_white:
                return True
        return False

    #  TODO: promotion method


class Rook(Piece):
    VALUE = 5
    IMAGE_WHITE = 'assets/Chess_rlt45.png'
    IMAGE_BLACK = 'assets/Chess_rdt45.png'

    def __init__(self, algebraic_notation: str, color: bool):
        self.__first_coordinates = algebraic_notation
        super().__init__(algebraic_notation, color)

    def __repr__(self):
        return f"R{self.square}"

    @property
    def value(self) -> int:
        return Rook.VALUE

    @property
    def has_moved(self) -> bool:
        return self.square != self.__first_coordinates

    @staticmethod
    def get_moves_no_board_test_static(indices: Tuple[int, int]) -> Set[Tuple[int, int]]:
        moves = set()
        curr_file, curr_rank = indices
        for rank in RANKS_IDX:
            moves.add((curr_file, rank))
        for file in FILES_IDX:
            moves.add((file, curr_rank))
        try:
            moves.remove(indices)
        except KeyError:
            pass
        return moves

    def get_moves_no_board(self) -> Set[Tuple[int, int]]:
        return self.get_moves_no_board_test_static(self.indices)

    @staticmethod
    def can_move_to_no_self_check_test_static(color: bool, move_from: str, move_to: str, game: Game) -> bool:
        curr_file, curr_rank = to_indices(move_from)
        new_file, new_rank = to_indices(move_to)
        #  Cull unconditionally unavailable moves
        if (new_file, new_rank) not in Rook.get_moves_no_board_test_static((curr_file, curr_rank)):
            return False

        dx, dy = new_file - curr_file, new_rank - curr_rank
        #  This is allowed because we know the rook must either move along the same file or same rank
        ds = dx if dx != 0 else dy
        sgn = int(copysign(1, ds))
        same_file = True if dx == 0 else False

        #  Make sure each square is empty between current position and new position
        if same_file:
            for rank in range(curr_rank + sgn, new_rank, sgn):
                if game.board.state[curr_file][rank] is not EMPTY:
                    return False
        else:
            for file in range(curr_file + sgn, new_file, sgn):
                if game.board.state[file][curr_rank] is not EMPTY:
                    return False

        #  Now just check that the square we are moving to is empty or an opposing piece
        if game.board.state[new_file][new_rank] is EMPTY or game.board.state[new_file][new_rank].color != color:
            return True
        return False

    def can_move_to_no_self_check_test(self, end: str, game: Game) -> bool:
        return self.can_move_to_no_self_check_test_static(self.color, self.square, end, game)


class Bishop(Piece):
    VALUE = 3
    IMAGE_WHITE = 'assets/Chess_blt45.png'
    IMAGE_BLACK = 'assets/Chess_bdt45.png'

    def __init__(self, algebraic_notation: str, color: bool):
        super().__init__(algebraic_notation, color)

    def __repr__(self):
        return f"B{self.square}"

    @property
    def value(self) -> int:
        return Bishop.VALUE

    @staticmethod
    def get_moves_no_board_test_static(indices: Tuple[int, int]) -> Set[Tuple[int, int]]:
        moves = set()
        file, rank = indices
        for i in range(len(FILES_IDX)):
            moves.add((file - i, rank - i))
            moves.add((file + i, rank + i))
            moves.add((file + i, rank - i))
            moves.add((file - i, rank + i))
        moves.remove(indices)
        return set(filter(lambda j: j in INDICES, moves))

    def get_moves_no_board(self) -> Set[Tuple[int, int]]:
        return self.get_moves_no_board_test_static(self.indices)

    @staticmethod
    def can_move_to_no_self_check_test_static(color: bool, move_from: str, move_to: str, game):
        curr_file, curr_rank = to_indices(move_from)
        new_file, new_rank = to_indices(move_to)
        if (new_file, new_rank) not in Bishop.get_moves_no_board_test_static((curr_file, curr_rank)):
            return False
        dx, dy = new_file - curr_file, new_rank - curr_rank
        dx_sgn, dy_sgn = int(copysign(1, dx)), int(copysign(1, dy))
        #  Make sure each square is empty between current position and new position
        counter = 1
        for file in range(curr_file + dx_sgn, new_file, dx_sgn):
            if game.board.state[file][curr_rank + counter * dy_sgn] is not EMPTY:
                return False
            counter += 1
        if game.board.state[new_file][new_rank] is EMPTY or game.board.state[new_file][new_rank].color != color:
            return True
        return False

    def can_move_to_no_self_check_test(self, end: str, game: Game) -> bool:
        return self.can_move_to_no_self_check_test_static(self.color, self.square, end, game)


class Knight(Piece):
    VALUE = 3
    IMAGE_WHITE = 'assets/Chess_nlt45.png'
    IMAGE_BLACK = 'assets/Chess_ndt45.png'

    def __init__(self, algebraic_notation: str, color: bool):
        super().__init__(algebraic_notation, color)

    def __repr__(self):
        return f"N{self.square}"

    @property
    def value(self) -> int:
        return Knight.VALUE

    def get_moves_no_board(self) -> Set[Tuple[int, int]]:
        moves = set()
        file, rank = self.indices
        moves.add((file + 2, rank + 1))
        moves.add((file + 2, rank - 1))
        moves.add((file + 1, rank + 2))
        moves.add((file + 1, rank - 2))
        moves.add((file - 2, rank + 1))
        moves.add((file - 2, rank - 1))
        moves.add((file - 1, rank + 2))
        moves.add((file - 1, rank - 2))
        return set(filter(lambda i: i in INDICES, moves))

    def can_move_to_no_self_check_test(self, end: str, game: Game) -> bool:
        new_file, new_rank = to_indices(end)
        if (new_file, new_rank) not in self.get_moves_no_board():
            return False
        if game.board.state[new_file][new_rank] is EMPTY or game.board.state[new_file][new_rank].color != self.color:
            return True
        return False


class Queen(Piece):
    VALUE = 10
    IMAGE_WHITE = 'assets/Chess_qlt45.png'
    IMAGE_BLACK = 'assets/Chess_qdt45.png'

    def __init__(self, algebraic_notation: str, color: bool):
        super().__init__(algebraic_notation, color)

    def __repr__(self):
        return f"Q{self.square}"

    @property
    def value(self) -> int:
        return Queen.VALUE

    def get_moves_no_board(self) -> Set[Tuple[int, int]]:
        moves = set()
        moves.update(Bishop.get_moves_no_board_test_static(self.indices))
        moves.update(Rook.get_moves_no_board_test_static(self.indices))
        return moves

    def can_move_to_no_self_check_test(self, end: str, game: Game) -> bool:
        return Rook.can_move_to_no_self_check_test_static(self.color, self.square, end, game) or (
            Bishop.can_move_to_no_self_check_test_static(self.color, self.square, end, game))


class King(Piece):
    VALUE = 0
    CAN_PIN = False
    IMAGE_WHITE = 'assets/Chess_klt45.png'
    IMAGE_BLACK = 'assets/Chess_kdt45.png'

    def __init__(self, algebraic_notation: str, color: bool):
        self.has_moved = False if (color == WHITE and algebraic_notation == 'e1') or (
                color == BLACK and algebraic_notation == 'e8') else True
        super().__init__(algebraic_notation, color)

    def __repr__(self):
        return f"K{self.square}"

    @property
    def value(self) -> int:
        return King.VALUE

    def get_moves_no_board(self) -> Set[Tuple[int, int]]:
        moves = set()
        file, rank = self.indices

        #  Regular moves
        moves.add((file - 1, rank - 1))
        moves.add((file - 1, rank))
        moves.add((file - 1, rank + 1))
        moves.add((file, rank + 1))
        moves.add((file + 1, rank + 1))
        moves.add((file + 1, rank))
        moves.add((file + 1, rank - 1))
        moves.add((file, rank - 1))

        #  Castle moves
        moves.add((file - 2, rank))
        moves.add((file + 2, rank))

        moves = set(filter(lambda i: i in INDICES, moves))
        return moves

    def can_castle(self, rook: Rook, game: Game) -> bool:
        if self.has_moved or rook.has_moved:
            return False
        sgn = int(copysign(1, rook.indices[0] - self.indices[0]))
        #  Test if squares between King and Rook are empty
        for file in range(self.indices[0] + sgn, self.indices[0] + 3 * sgn, sgn):
            square = from_indices((file, self.indices[1]))
            if game[square] is not EMPTY:
                return False
        #  Test if King is currently under check or if opponent has line-of-sight on castling squares
        threats = [piece for piece in game.board if piece.color != self.color]
        for file in range(self.indices[0], self.indices[0] + 3 * sgn, sgn):
            square = from_indices((file, self.indices[1]))
            for threat in threats:
                if threat.can_move_to_no_self_check_test(square, game):
                    return False
        return True

    def can_move_to_no_self_check_test(self, end: str, game: Game) -> bool:
        new_file, new_rank = to_indices(end)
        if (new_file, new_rank) not in self.get_moves_no_board():
            return False
        if game.board.state[new_file][new_rank] is EMPTY or game.board.state[new_file][new_rank].color != self.color:
            return True
        return False
