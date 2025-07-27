from typing import Any

import numpy as np
from numpy.typing import NDArray
from pymoo.core.problem import ElementwiseProblem

from poketactician.engine.selector import ObjectiveSelector


class PokemonProblem(ElementwiseProblem):
    def __init__(
        self,
        objectives: ObjectiveSelector,
        lm: NDArray[np.bool_],
        n_pokemon: int,
        n_moves: int,
        repeat_pokemon: bool = False,
        pokemon_in_team: int = 6,
        **kwargs: Any,  # noqa: ANN401
    ) -> None:
        self.n_pokemon = n_pokemon
        self.n_moves = n_moves
        self.objectives = objectives
        self.LM = lm.astype(bool)
        self.repeat_pokemon = repeat_pokemon
        self.pokemon_in_team = pokemon_in_team
        super().__init__(
            n_var=self.pokemon_in_team + self.pokemon_in_team * 4,  # Num pokemon + Num Pokemon * 4 moves
            n_obj=self.objectives.n_obj,
            n_ieq_constr=self.pokemon_in_team * 4
            + self.pokemon_in_team
            + 1 * self.repeat_pokemon,  # The 4 moves of each 6 pokemon must be learnable. Each pokemon has 4 different moves
            xl=0,
            xu=n_pokemon,
            type_var=np.uint16,
        )

    def _evaluate(self, x: NDArray[np.uint16], out: dict, *args, **kwargs) -> None:  # noqa: N803
        F = []
        G = []
        ind = x.copy()

        x = ind[: self.pokemon_in_team]
        y = ind[self.pokemon_in_team :].reshape(self.pokemon_in_team, 4)

        # === Objectives ===
        # x contains the row indexes, y contains the column indexes for ME
        # For each pair (xi, yi), sum ME[xi, yi]

        prefilter_pokemon_rows = np.repeat(x, 4)
        prefilter_move_columns = y.flatten()
        # Filter out moves with value -1 and their corresponding pokemon_rows
        valid_mask = prefilter_move_columns != -1
        pokemon_rows = prefilter_pokemon_rows[valid_mask]
        move_columns = prefilter_move_columns[valid_mask]
        F.append(self.objectives.evaluate(x, y))  # negative = maximize

        # === Constraints ===
        constraints = []

        # Moves in the positions of x_i and y_i are learnable: 1 - LM_xi,yi ≤ 0
        constraints += list((1 - self.LM[pokemon_rows, move_columns]).flatten())

        # Not repeated moves: len(yi) - len(set(yi)) ≤ 0
        constraints += list((np.apply_along_axis(lambda row: len(row[row >= 0]) - len(set(row[row >= 0])), 1, y)))

        # no repeated Pokemon: len(x) - len(set(x)) ≤ 0
        if self.repeat_pokemon:
            constraints += list((len(set(x)) - len(x)).flatten())

        G.append(constraints)

        out["F"] = np.array(F)
        out["G"] = np.array(G)
