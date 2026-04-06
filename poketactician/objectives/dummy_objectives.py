import numpy as np

from poketactician.config import ATK_STAT_INDEX, EMPTY_MOVE_SENTINEL, NUMBER_OF_MOVES_SLOTS, NUMBER_OF_STATS, SPA_STAT_INDEX, STAB_BONUS
from poketactician.registry import register_objective


@register_objective(data_mapping={"me": "moves_category"})
def test_objective(x: np.ndarray, y: np.ndarray, me: np.ndarray) -> int:
    """Objective function that sums the effectiveness of moves selected by y."""
    prefilter_move_columns = y.flatten()
    valid_mask = prefilter_move_columns != EMPTY_MOVE_SENTINEL
    move_columns = prefilter_move_columns[valid_mask]
    return me[:, move_columns].sum()


@register_objective(data_mapping={"me": "moves_category"})
def test_objective2(x: np.ndarray, y: np.ndarray, me: np.ndarray) -> int:
    """Objective function that returns the maximum effectiveness of moves selected by y."""
    prefilter_move_columns = y.flatten()
    valid_mask = prefilter_move_columns != EMPTY_MOVE_SENTINEL
    move_columns = prefilter_move_columns[valid_mask]
    return me[:, move_columns].max()


@register_objective()
def test_objective3(x: np.ndarray, y: np.ndarray, moves_category: np.ndarray) -> int:
    """Objective function that returns the negative sum of effectiveness of moves selected by y."""
    prefilter_move_columns = y.flatten()
    valid_mask = prefilter_move_columns != EMPTY_MOVE_SENTINEL
    move_columns = prefilter_move_columns[valid_mask]
    return -moves_category[:, move_columns].sum()


# Selects Attack and Special Attack from the stat vector
_ATK_STAT_SELECTOR = np.zeros((NUMBER_OF_STATS, 2), dtype=int)
_ATK_STAT_SELECTOR[ATK_STAT_INDEX, 0] = 1
_ATK_STAT_SELECTOR[SPA_STAT_INDEX, 1] = 1


@register_objective()
def expected_damage(
    x: np.ndarray,
    y: np.ndarray,
    pokemon_stats: np.ndarray,
    moves_category: np.ndarray,
    move_types: np.ndarray,
    pokemon_types: np.ndarray,
) -> int:
    """Objective function that calculates expected damage based on selected moves and Pokemon stats."""
    stab_matrix = STAB_BONUS * np.dot(pokemon_types[x], move_types.T) + 1  # Shape: (team_size, n_moves)
    learned_moves_mask = np.zeros_like(stab_matrix, dtype=bool)
    flat_moves = y.flatten()
    valid = flat_moves != EMPTY_MOVE_SENTINEL
    team_idx = np.repeat(np.arange(len(x)), NUMBER_OF_MOVES_SLOTS)[valid]
    learned_moves_mask[team_idx, flat_moves[valid]] = True
    selection_stab = stab_matrix * learned_moves_mask  # STAB for selected moves only
    damage_per_class = np.dot(selection_stab, moves_category.T)  # Shape: (team_size, n_classes)
    team_attack_stats = np.dot(pokemon_stats[x], _ATK_STAT_SELECTOR)  # Shape: (team_size, 2)
    damage_per_pokemon = damage_per_class * team_attack_stats
    return int(damage_per_pokemon.sum())
