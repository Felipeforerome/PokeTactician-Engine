from typing import Any

import numpy as np
from numpy.typing import NDArray
from pymoo.core.problem import ElementwiseProblem

from poketactician.config import EMPTY_MOVE_SENTINEL, MAX_NUMBER_OF_POKEMON, NUMBER_OF_MOVES_SLOTS
from poketactician.engine.selector import ObjectiveSelector


class PokemonProblem(ElementwiseProblem):
    def __init__(
        self,
        objectives: ObjectiveSelector,
        lm: NDArray[np.bool_],
        n_pokemon: int,
        n_moves: int,
        unique_pokemon_only: bool = False,
        pokemon_in_team: int = MAX_NUMBER_OF_POKEMON,
        **kwargs: Any,  # noqa: ANN401
    ) -> None:
        self.n_pokemon = n_pokemon
        self.n_moves = n_moves
        self.objectives = objectives
        self.LM = lm.astype(bool)
        self.unique_pokemon_only = unique_pokemon_only
        self.pokemon_in_team = pokemon_in_team
        super().__init__(
            n_var=self.pokemon_in_team + self.pokemon_in_team * NUMBER_OF_MOVES_SLOTS,  # Num pokemon + Num Pokemon * NUMBER_OF_MOVES_SLOTS moves
            n_obj=self.objectives.n_obj,
            n_ieq_constr=self.pokemon_in_team * NUMBER_OF_MOVES_SLOTS
            + self.pokemon_in_team
            + 1 * (self.unique_pokemon_only),  # The 4 moves of each 6 pokemon must be learnable. Each pokemon has 4 different moves
            xl=0,
            xu=n_pokemon,
            type_var=np.int16,
        )

    def _evaluate(self, x: NDArray[np.int16], out: dict, *args, **kwargs) -> None:  # noqa: N803
        F = []
        G = []
        ind = x.copy()

        x = ind[: self.pokemon_in_team]
        y = ind[self.pokemon_in_team :].reshape(self.pokemon_in_team, NUMBER_OF_MOVES_SLOTS)

        # === Objectives ===
        # x contains the row indexes, y contains the column indexes for ME
        # For each pair (xi, yi), sum ME[xi, yi]

        prefilter_pokemon_rows = np.repeat(x, NUMBER_OF_MOVES_SLOTS)
        prefilter_move_columns = y.flatten()
        # Filter out moves with value EMPTY_MOVE_SENTINEL and their corresponding pokemon_rows
        valid_mask = prefilter_move_columns != EMPTY_MOVE_SENTINEL
        pokemon_rows = prefilter_pokemon_rows[valid_mask]
        move_columns = prefilter_move_columns[valid_mask]
        F.append(self.objectives.evaluate(x, y))  # negative = maximize

        # === Constraints ===
        constraints = []

        # Moves in the positions of x_i and y_i are learnable: 1 - LM_xi,yi ≤ 0
        constraints += list((1 - self.LM[pokemon_rows, move_columns]).flatten())

        # Not repeated moves: len(yi) - len(set(yi)) ≤ 0
        constraints += list((np.apply_along_axis(lambda row: len(row[row != EMPTY_MOVE_SENTINEL]) - len(set(row[row != EMPTY_MOVE_SENTINEL])), 1, y)))

        # no repeated Pokemon: len(x) - len(set(x)) ≤ 0
        if self.unique_pokemon_only:
            constraints.append(len(x) - len(set(x)))

        G.append(constraints)

        out["F"] = np.array(F)
        out["G"] = np.array(G)
