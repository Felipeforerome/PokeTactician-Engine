import numpy as np
from numpy.typing import NDArray
from pymoo.core.sampling import Sampling

from poketactician.engine.problem import PokemonProblem


class PokemonTeamSampling(Sampling):
    def __init__(self, random_state: np.random.Generator, pre_selected: dict | None = None) -> None:
        super().__init__()
        self.random_state = random_state
        self.pre_selected_moves = tuple(np.array(pre_selected[i], dtype=np.int16) for i in pre_selected.keys()) if pre_selected is not None else None
        self.pre_selected_pokemon = tuple(i for i in pre_selected.keys()) if pre_selected is not None else None

    def _do(self, problem: PokemonProblem, n_samples: int, **kwargs) -> NDArray[np.int16]:
        individuals = []

        for _ in range(n_samples):
            team = []
            # If pre-selected Pokémon are provided, use them
            if self.pre_selected_pokemon is not None:
                team.extend(self.pre_selected_pokemon)

            # (1) Select remaining unique Pokémon
            remaining_team = self.random_state.choice(
                [i for i in range(problem.n_pokemon) if i not in team], problem.pokemon_in_team - len(team), replace=False
            )
            team.extend(remaining_team)

            # (2) Assign 4 legal moves to each selected Pokémon
            moves = np.zeros((problem.pokemon_in_team, 4), dtype=np.int16)

            for j, i in enumerate(team):
                legal_moves = np.where(problem.LM[i])[0]
                chosen = -1 * np.ones(4, dtype=np.int16)
                selected = self.pre_selected_moves[j] if self.pre_selected_moves is not None and j < len(self.pre_selected_moves) else []
                num_random_moves = 4 - len(selected)
                if len(legal_moves) >= num_random_moves:
                    random_moves = self.random_state.choice(legal_moves, size=num_random_moves, replace=False)
                else:
                    # Optional: fallback to random other Pokémon if not enough moves
                    random_moves = self.random_state.choice(legal_moves, size=len(legal_moves), replace=False)
                selected = np.append(selected, random_moves)
                chosen[: selected.shape[0]] = selected
                moves[j] = chosen

            # Flatten and concatenate
            indiv = np.concatenate([team, moves.flatten()])
            individuals.append(indiv)

        return np.array(individuals)
