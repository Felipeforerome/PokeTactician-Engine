"""Mutation operators for Pokemon team optimization.

This module implements custom mutation strategies for evolving Pokemon teams,
including both Pokemon substitution and move set modifications.
"""

import numpy as np
from numpy.typing import NDArray
from pymoo.core.mutation import Mutation

from poketactician.config import DEFAULT_MUTATION_PROB_MOVE, DEFAULT_MUTATION_PROB_POKEMON, EMPTY_MOVE_SENTINEL, NUMBER_OF_MOVES_SLOTS
from poketactician.engine.problem import PokemonProblem
from poketactician.utils import get_random_moves


class PokemonMutation(Mutation):
    """Custom mutation operator for Pokemon team optimization.

    This mutation operator applies two types of mutations:
    1. Pokemon mutation: Replaces entire Pokemon in the team
    2. Move mutation: Modifies individual moves for Pokemon in the team

    Both mutation types respect pre-selected Pokemon and moves that should
    remain fixed during optimization.
    """

    def __init__(
        self,
        random_state: np.random.Generator,
        prob_pokemon: float | None = None,
        prob_move: float | None = None,
        pre_selected: dict | None = None,
    ) -> None:
        """Initialize the Pokemon mutation operator.

        Args:
            random_state: NumPy random number generator for reproducibility
            prob_pokemon: Probability of mutating each Pokemon in the team (default: 0.01)
            prob_move: Probability of mutating each individual move (default: 0.001)
            pre_selected: Dictionary mapping team positions to pre-selected Pokemon/moves
                         that should not be mutated (default: None)
        """
        super().__init__()
        self.random_state = random_state
        self.prob_pokemon = prob_pokemon if prob_pokemon is not None else DEFAULT_MUTATION_PROB_POKEMON
        self.prob_move = prob_move if prob_move is not None else DEFAULT_MUTATION_PROB_MOVE
        self.pre_selected = pre_selected if pre_selected is not None else {}

    def pokemon_mutation(self, x: NDArray[np.int16], y: NDArray[np.int16], lm: NDArray[np.bool_]) -> tuple[NDArray[np.int16], NDArray[np.int16]]:
        """Mutate Pokemon in the team by replacing them with different Pokemon.

        Args:
            x: Array of Pokemon indices representing the current team
            y: 2D array of move indices for each Pokemon (shape: [team_size, NUMBER_OF_MOVES_SLOTS])
            lm: Legal moves matrix indicating valid moves for each Pokemon

        Returns:
            Tuple of (mutated_team, mutated_moves) where both are updated arrays
        """
        # Get all Pokemon not currently in the team as candidates for mutation
        not_chosen_pokemon = [i for i in range(lm.shape[0]) if i not in x]
        possible_new_pokemon = self.random_state.choice(not_chosen_pokemon, size=x.shape[0], replace=False)

        # Determine which Pokemon to mutate based on probability
        mutated_pokemon_mask = self.random_state.random(x.shape[0]) < self.prob_pokemon

        # Protect pre-selected Pokemon from mutation
        for i in range(len(self.pre_selected.keys())):
            mutated_pokemon_mask[i] = False

        # Apply mutations: replace selected Pokemon with new ones
        mutated_team = np.where(
            mutated_pokemon_mask,
            possible_new_pokemon,
            x,
        )

        # Update moves for any newly added Pokemon
        mutated_moves = y.copy()
        for j, i in enumerate(mutated_team):
            if mutated_pokemon_mask[j]:
                # Generate new random legal moves for the replacement Pokemon
                mutated_moves[j] = get_random_moves(lm, i, self.random_state)
        return mutated_team, mutated_moves

    def move_mutation(self, x: NDArray[np.int16], y: NDArray[np.int16], lm: NDArray[np.bool_]) -> NDArray[np.int16]:
        """Mutate individual moves for Pokemon in the team.

        Args:
            x: Array of Pokemon indices representing the current team
            y: 2D array of move indices for each Pokemon (shape: [team_size, NUMBER_OF_MOVES_SLOTS])
            lm: Legal moves matrix indicating valid moves for each Pokemon

        Returns:
            Updated move array with mutations applied
        """
        pokemon_in_team = x.shape[0]

        # Determine which moves to mutate based on probability
        mutated_moves_mask = self.random_state.random((y.shape[0], y.shape[1])) < self.prob_move

        # Protect pre-selected moves from mutation
        for pos, pre_selected_moves in enumerate(self.pre_selected.values()):
            mutated_moves_mask[pos] &= ~np.isin(y[pos], pre_selected_moves)

        # Find which Pokemon have at least one move being mutated
        rows_with_mutations = np.any(mutated_moves_mask, axis=1)
        pokemon_with_mutations = x[rows_with_mutations]

        # Generate new random moves for Pokemon that need mutations
        possible_new_moves = np.zeros((pokemon_in_team, NUMBER_OF_MOVES_SLOTS), dtype=np.int16)
        modified_LM = self.modify_lm(x, y, lm)
        for i in pokemon_with_mutations:
            possible_new_moves[np.where(x == i)[0][0]] = get_random_moves(modified_LM, i, self.random_state)

        # Apply mutations only where valid moves are available (not empty sentinel)
        mutated_moves = np.where(
            np.logical_and(mutated_moves_mask, possible_new_moves != EMPTY_MOVE_SENTINEL),
            possible_new_moves,
            y,
        )
        return mutated_moves

    def modify_lm(self, x: NDArray[np.int16], y: NDArray[np.int16], lm: NDArray[np.bool_]) -> NDArray[np.bool_]:
        """Modify the legal moves matrix to exclude currently equipped moves.

        This prevents the mutation from selecting the same moves already equipped
        on a Pokemon, ensuring meaningful mutations when Pokemon have many available moves.

        Args:
            x: Array of Pokemon indices representing the current team
            y: 2D array of move indices for each Pokemon (shape: [team_size, NUMBER_OF_MOVES_SLOTS])
            lm: Legal moves matrix indicating valid moves for each Pokemon

        Returns:
            Modified legal moves matrix with current moves marked as unavailable
        """
        modified_LM = lm.copy()
        num_moves_available = modified_LM.sum(axis=1)[x]

        # For each Pokemon in the team
        for x_i, x_val in enumerate(x):
            curren_available_moves = num_moves_available[x_i]
            # Mark already-equipped moves as unavailable if Pokemon has more than 4 moves
            for y_i in y[x_i]:
                if y_i == EMPTY_MOVE_SENTINEL:
                    continue  # Skip empty move slots
                if curren_available_moves > NUMBER_OF_MOVES_SLOTS:
                    modified_LM[x_val, y_i] = 0  # Mark move as unavailable
                    curren_available_moves -= 1
                else:
                    break  # Stop if Pokemon only has 4 moves total
        return modified_LM

    def _do(self, problem: PokemonProblem, X: NDArray[np.int16], **kwargs) -> NDArray[np.int16]:  # noqa: N803
        """Apply mutation to a population of solutions.

        This is the main entry point called by pymoo's evolutionary algorithm.
        It applies both Pokemon and move mutations to each individual in the population.

        Args:
            problem: The PokemonProblem instance containing game constraints
            X: Population array where each row is an individual solution
               Format: [pokemon_ids..., move_ids_flattened...]
            **kwargs: Additional arguments (unused)

        Returns:
            Mutated population array with the same shape as input
        """
        for ind in X:
            # Split individual into Pokemon team and move sets
            x = ind[: problem.pokemon_in_team]  # Pokemon indices
            y = ind[problem.pokemon_in_team :].reshape(problem.pokemon_in_team, NUMBER_OF_MOVES_SLOTS)  # Move indices

            mutated_team = x.copy()
            mutated_moves = y.copy()

            # Apply Pokemon mutation (may replace entire Pokemon)
            mutated_team, mutated_moves = self.pokemon_mutation(x, y, problem.LM)

            # Apply move mutation (changes individual moves)
            mutated_moves = self.move_mutation(mutated_team, mutated_moves, problem.LM)

            # Write mutated values back to the individual
            ind[: problem.pokemon_in_team] = mutated_team
            ind[problem.pokemon_in_team :] = mutated_moves.flatten()

        return X
