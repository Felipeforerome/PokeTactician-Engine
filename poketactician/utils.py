from typing import Any, Optional, Protocol

import numpy as np
from numpy.typing import NDArray


def get_random_moves(lm: np.ndarray, i: int, random_state: np.random.Generator) -> np.ndarray:
    legal_moves = np.where(lm[i])[0]
    chosen = -1 * np.ones(4, dtype=np.int16)
    if len(legal_moves) >= 4:
        selected = random_state.choice(legal_moves, size=4, replace=False)
    else:
        # Optional: fallback to random other Pokémon if not enough moves
        selected = random_state.choice(legal_moves, size=len(legal_moves), replace=False)
    chosen[: selected.shape[0]] = selected
    return chosen


class StrictResults(Protocol):
    F: NDArray[np.float64]
    X: NDArray[np.int16]
    history: Optional[list[Any]]
    algorithm: Any


class ResultsWithHistory(StrictResults, Protocol):
    history: list[Any]


class DecisionFunction(Protocol):
    def __call__(self, x: NDArray[np.int16]) -> NDArray[np.int16]: ...
