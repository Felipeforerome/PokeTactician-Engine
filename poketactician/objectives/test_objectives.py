import numpy as np

from poketactician.registry import register_objective


@register_objective()
def test_objective(x: np.ndarray, y: np.ndarray, me: np.ndarray) -> int:
    """Objective function that sums the effectiveness of moves selected by y."""
    prefilter_move_columns = y.flatten()
    valid_mask = prefilter_move_columns != -1
    move_columns = prefilter_move_columns[valid_mask]
    return me[:, move_columns].sum()


@register_objective()
def test_objective2(x: np.ndarray, y: np.ndarray, me: np.ndarray) -> int:
    """Objective function that returns the maximum effectiveness of moves selected by y."""
    prefilter_move_columns = y.flatten()
    valid_mask = prefilter_move_columns != -1
    move_columns = prefilter_move_columns[valid_mask]
    return me[:, move_columns].max()
