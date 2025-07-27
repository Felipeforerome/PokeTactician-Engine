import numpy as np
from numpy.typing import NDArray
from pymoo.core.crossover import Crossover

from poketactician.engine.problem import PokemonProblem


class PokemonCrossover(Crossover):
    def __init__(self, random_state: np.random.Generator, prob_pokemon: float = 0.5) -> None:
        super().__init__(2, 2)  # 2 parents → 2 offspring
        self.prob_pokemon = prob_pokemon
        self.random_state = random_state

    def _do(self, problem: PokemonProblem, X: NDArray[np.uint16], **kwargs) -> NDArray[np.uint16]:  # noqa: N803
        _, n_matings, _ = X.shape
        pokemon_in_team = problem.pokemon_in_team

        offspring = np.empty_like(X)

        for k in range(n_matings):
            parent1 = X[0][k]
            parent2 = X[1][k]

            # CASE 1: If both parents are identical, just copy them
            if np.all(parent1 == parent2):
                offspring[0][k] = parent1.copy()
                offspring[1][k] = parent2.copy()
                continue

            # Split into X and Y
            x1, y1 = (
                parent1[:pokemon_in_team],
                parent1[pokemon_in_team:].reshape(pokemon_in_team, 4),
            )
            x2, y2 = (
                parent2[:pokemon_in_team],
                parent2[pokemon_in_team:].reshape(pokemon_in_team, 4),
            )

            parent1_src1 = self.random_state.random() < self.prob_pokemon  # True if child1 is based on parent 1, False if based on parent 2
            parent1_src2 = self.random_state.random() > self.prob_pokemon  # True if child2 is based on parent 1, False if based on parent 2
            child1 = parent1.copy() if parent1_src1 else parent2.copy()
            child2 = parent1.copy() if parent1_src2 else parent2.copy()

            child1_x, child1_y = (
                child1[:pokemon_in_team],
                child1[pokemon_in_team:].reshape(pokemon_in_team, 4),
            )
            child2_x, child2_y = (
                child2[:pokemon_in_team],
                child2[pokemon_in_team:].reshape(pokemon_in_team, 4),
            )

            # --- Perform crossover on x (pokémon IDs) ---
            n_crossovers_max = self.random_state.integers(1, pokemon_in_team - 1)
            common = set(x1) & set(x2)
            indexes_from1 = x2 if parent1_src1 else x1
            indexes_from2 = x2 if parent1_src2 else x1
            indices1 = [i for i in range(len(x1)) if indexes_from1[i] not in common]
            indices2 = [j for j in range(len(x2)) if indexes_from2[j] not in common]
            self.random_state.shuffle(indices1)
            self.random_state.shuffle(indices2)
            n_crossovers = min(n_crossovers_max, len(indices1), len(indices2))
            done_crossovers = 0
            for i1, i2 in zip(indices1[:n_crossovers], indices2[:n_crossovers]):
                val1 = x2[i1] if parent1_src1 else x1[i1]
                val2 = x2[i2] if parent1_src2 else x1[i2]
                if val1 not in child1_x:
                    if val2 not in child2_x:
                        m1 = y2[i1] if parent1_src1 else y1[i1]
                        m2 = y2[i2] if parent1_src2 else y1[i2]
                        child1_x[i1], child2_x[i2] = val1, val2
                        child1_y[i1], child2_y[i2] = (
                            m1.copy(),
                            m2.copy(),
                        )
                        done_crossovers += 1
                        # print(f"Done crossovers: {done_crossovers}/{n_crossovers}")

            # Combine x and y back into flattened vectors
            offspring[0][k] = np.concatenate([child1_x, child1_y.flatten()])
            offspring[1][k] = np.concatenate([child2_x, child2_y.flatten()])

        return offspring
