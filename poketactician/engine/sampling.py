"""Sampling operators for Pokemon team optimization.

This module implements custom sampling strategies for generating initial Pokemon teams
with legal move sets for evolutionary optimization.
"""

import numpy as np
from numpy.typing import NDArray
from pymoo.core.sampling import Sampling

from poketactician.config import NUMBER_OF_MOVES_SLOTS
from poketactician.engine.problem import PokemonProblem


class PokemonTeamSampling(Sampling):
    """Custom sampling operator for Pokemon team optimization.

    This sampling operator generates random Pokemon teams while respecting constraints:
    - Unique Pokemon selection (no duplicates in team)
    - Legal move assignments (only moves the Pokemon can learn)
    - Pre-selected Pokemon/moves preservation (if specified)
    """

    def __init__(self, random_state: np.random.Generator, pre_selected: dict | None = None) -> None:
        """Initialize the Pokemon team sampling operator.

        Args:
            random_state: NumPy random number generator for reproducibility
            pre_selected: Dictionary mapping team positions to pre-selected Pokemon/moves
                         Format: {position: [move_ids]} where position also implies the Pokemon
                         (default: None)
        """
        super().__init__()
        self.random_state = random_state
        self.pre_selected_moves = tuple(np.array(pre_selected[i], dtype=np.int16) for i in pre_selected.keys()) if pre_selected is not None else None
        self.pre_selected_pokemon = tuple(i for i in pre_selected.keys()) if pre_selected is not None else None

    def sample_team(self, problem: PokemonProblem) -> list[int]:
        """Sample a team of unique Pokemon.

        Constructs a team by first including any pre-selected Pokemon, then
        randomly selecting remaining Pokemon to fill the team.

        Args:
            problem: The PokemonProblem instance containing game constraints

        Returns:
            List of Pokemon indices representing the team
        """
        team = []

        # Include pre-selected Pokemon if provided
        if self.pre_selected_pokemon is not None:
            team.extend(self.pre_selected_pokemon)

        # Select remaining unique Pokemon to complete the team
        remaining_team = self.random_state.choice([i for i in range(problem.n_pokemon) if i not in team], problem.pokemon_in_team - len(team), replace=False)
        team.extend(remaining_team)

        return team

    def sample_moves(self, problem: PokemonProblem, team: list[int]) -> NDArray[np.int16]:
        """Sample legal moves for each Pokemon in the team.

        Assigns 4 moves to each Pokemon, respecting pre-selected moves and
        ensuring all moves are legal for that Pokemon.

        Args:
            problem: The PokemonProblem instance containing legal move constraints
            team: List of Pokemon indices representing the team

        Returns:
            2D array of move indices (shape: [team_size, NUMBER_OF_MOVES_SLOTS])
        """
        moves = np.zeros((problem.pokemon_in_team, NUMBER_OF_MOVES_SLOTS), dtype=np.int16)

        for j, pokemon_id in enumerate(team):
            legal_moves = np.where(problem.LM[pokemon_id])[0]
            chosen = -1 * np.ones(NUMBER_OF_MOVES_SLOTS, dtype=np.int16)

            # Get pre-selected moves for this position if available
            selected = self.pre_selected_moves[j] if self.pre_selected_moves is not None and j < len(self.pre_selected_moves) else []
            num_random_moves = NUMBER_OF_MOVES_SLOTS - len(selected)

            # Exclude already selected moves from legal moves pool
            available_moves = np.array([move for move in legal_moves if move not in selected])

            # Sample remaining moves randomly from available legal moves
            if len(available_moves) >= num_random_moves:
                random_moves = self.random_state.choice(available_moves, size=num_random_moves, replace=False)
            else:
                # Fallback: use all available legal moves if less than needed
                random_moves = self.random_state.choice(available_moves, size=len(available_moves), replace=False)

            selected = np.append(selected, random_moves)
            chosen[: selected.shape[0]] = selected
            moves[j] = chosen

        return moves

    def _do(self, problem: PokemonProblem, n_samples: int, **kwargs) -> NDArray[np.int16]:
        """Generate initial population of Pokemon teams.

        This is the main entry point called by pymoo's evolutionary algorithm.
        It generates n_samples random teams, each with randomly assigned legal moves.

        Args:
            problem: The PokemonProblem instance containing game constraints
            n_samples: Number of individuals to generate
            **kwargs: Additional arguments (unused)

        Returns:
            Population array where each row is an individual solution
            Format: [pokemon_ids..., move_ids_flattened...]
        """
        individuals = []

        for _ in range(n_samples):
            # Sample a team of unique Pokemon
            team = self.sample_team(problem)

            # Assign legal moves to each Pokemon in the team
            moves = self.sample_moves(problem, team)

            # Flatten and concatenate team and moves into single individual
            indiv = np.concatenate([team, moves.flatten()])
            individuals.append(indiv)

        return np.array(individuals)
