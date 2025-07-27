import numpy as np
from numpy.typing import NDArray
from pymoo.core.mutation import Mutation

from poketactician.engine.problem import PokemonProblem
from poketactician.utils import get_random_moves


class PokemonMutation(Mutation):
    def __init__(self, random_state: np.random.Generator, prob_pokemon: float = 0.01, prob_move: float = 0.001) -> None:
        super().__init__()
        self.random_state = random_state
        self.prob_pokemon = prob_pokemon
        self.prob_move = prob_move

    def pokemon_mutation(self, x: NDArray[np.uint16], y: NDArray[np.int16], lm: NDArray[np.bool_]) -> tuple[NDArray[np.uint16], NDArray[np.int16]]:
        not_chosen_pokemon = [i for i in range(lm.shape[0]) if i not in x]
        possible_new_pokemon = self.random_state.choice(not_chosen_pokemon, size=x.shape[0], replace=False)

        mutated_pokemon_mask = self.random_state.random(x.shape[0]) < self.prob_pokemon
        mutated_team = np.where(
            mutated_pokemon_mask,
            possible_new_pokemon,
            x,
        )

        mutated_moves = y.copy()
        for j, i in enumerate(mutated_team):
            if mutated_pokemon_mask[j]:
                mutated_moves[j] = get_random_moves(lm, i, self.random_state)
        return mutated_team, mutated_moves

    def move_mutation(self, x: NDArray[np.uint16], y: NDArray[np.int16], lm: NDArray[np.bool_]) -> NDArray[np.int16]:
        pokemon_in_team = x.shape[0]
        mutated_moves_mask = self.random_state.random((y.shape[0], y.shape[1])) < self.prob_move
        rows_with_mutations = np.any(mutated_moves_mask, axis=1)
        pokemon_with_mutations = x[rows_with_mutations]
        possible_new_moves = np.zeros((pokemon_in_team, 4), dtype=np.int16)
        modified_LM = self.modify_lm(x, y, lm)
        for i in pokemon_with_mutations:
            possible_new_moves[np.where(x == i)[0][0]] = get_random_moves(modified_LM, i, self.random_state)
        mutated_moves = np.where(
            np.logical_and(mutated_moves_mask, possible_new_moves >= 0),
            possible_new_moves,
            y,
        )
        return mutated_moves

    def modify_lm(self, x: NDArray[np.uint16], y: NDArray[np.int16], lm: NDArray[np.bool_]) -> NDArray[np.bool_]:
        modified_LM = lm.copy()
        num_moves_available = modified_LM.sum(axis=1)[x]
        for x_i, x_val in enumerate(x):
            curren_available_moves = num_moves_available[x_i]
            for y_i in y[x_i]:
                if curren_available_moves > 4:
                    modified_LM[x_val, y_i] = 0
                    curren_available_moves -= 1
                else:
                    break
        return modified_LM

    def _do(self, problem: PokemonProblem, X: NDArray[np.uint16], **kwargs) -> NDArray[np.uint16]:  # noqa: N803
        for ind in X:
            x = ind[: problem.pokemon_in_team]
            y = ind[problem.pokemon_in_team :].reshape(problem.pokemon_in_team, 4)
            mutated_team = x.copy()
            mutated_moves = y.copy()

            mutated_team, mutated_moves = self.pokemon_mutation(x, y, problem.LM)

            # ==== Move mutation ====
            mutated_moves = self.move_mutation(mutated_team, mutated_moves, problem.LM)

            ind[: problem.pokemon_in_team] = mutated_team
            ind[problem.pokemon_in_team :] = mutated_moves.flatten()

        return X
