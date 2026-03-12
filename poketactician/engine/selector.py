from typing import Collection

import numpy as np

from poketactician.config import OBJECTIVE_REGISTRY


class ObjectiveSelector:
    def __init__(self, objective_names: Collection[str]) -> None:
        assert all(name in OBJECTIVE_REGISTRY for name in objective_names), (
            f"Some objectives are not registered: {set(objective_names) - set(OBJECTIVE_REGISTRY.keys())}"
        )

        if len(objective_names) == 0:
            raise ValueError("At least one objective must be provided")
        self.objectives = [OBJECTIVE_REGISTRY[name]() for name in objective_names]
        self.n_obj = len(self.objectives)

    def evaluate(self, x: np.ndarray, y: np.ndarray) -> list:
        return [-obj(x, y) for obj in self.objectives]
