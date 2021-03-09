from typing import Set, Tuple
from chessberry.chess import from_indices


def to_alg_set(indices_set: Set[Tuple[int, int]]) -> Set[str]:
    alg_set = set()
    for indices in indices_set:
        alg_set.add(from_indices(indices))

    return alg_set

