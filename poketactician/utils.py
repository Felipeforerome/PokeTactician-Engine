import numpy as np


def get_random_moves(lm: np.ndarray, i: int, random_state: np.random.Generator) -> np.ndarray[np.int16]:
    legal_moves = np.where(lm[i])[0]
    chosen = -1 * np.ones(4, dtype=np.int16)
    if len(legal_moves) >= 4:
        selected = random_state.choice(legal_moves, size=4, replace=False)
    else:
        # Optional: fallback to random other Pokémon if not enough moves
        selected = random_state.choice(legal_moves, size=len(legal_moves), replace=False)
    chosen[: selected.shape[0]] = selected
    return chosen
