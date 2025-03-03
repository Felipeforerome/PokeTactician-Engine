import time
from copy import deepcopy
from functools import reduce
from typing import Callable, Tuple

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from .Colony import Colony
from .glob_var import CooperationStats, Q, alpha, beta, rho
from .models.Pokemon import Pokemon
from .models.Team import Team
from .utils import dominated_candidate_set


class MOACO:
    """
    Multi-Objective Ant Colony Optimization (MOACO) class for optimizing team composition in Pokemon battles.

    Args:
        totalPopulation (int): The total population size.
        objFuncs_Q_rho (List[Tuple[Callable, float, float]]): A list of tuples containing the objective functions,
            pheromone decay rate (Q), and pheromone evaporation rate (rho).
        pokemonPop (List[Any]): A list of Pokemon objects representing the available Pokemon population.
        preSelected (List[int]): A list of pre-selected Pokemon IDs.
        alpha (float): The alpha parameter for the ant colony optimization algorithm.
        beta (float): The beta parameter for the ant colony optimization algorithm.
        cooperation_strategy (int, optional): The ID of the cooperation strategy to use. Defaults to 1.

    Raises:
        ValueError: If totalPopulation is not a positive integer or if alpha or beta are negative.

    Attributes:
        totalPopulation (int): The total population size.
        objFuncs_Q_rho (List[Tuple[Callable, float, float]]): A list of tuples containing the objective functions,
            pheromone decay rate (Q), and pheromone evaporation rate (rho).
        cooperationID (int): The ID of the cooperation strategy used.
        pokemonPop (List[Any]): A list of Pokemon objects representing the available Pokemon population, with preselected pokemon at the top.
        preSelected (List[int]): A list of pre-selected Pokemon IDs.
        alpha (float): The alpha parameter for the ant colony optimization algorithm.
        beta (float): The beta parameter for the ant colony optimization algorithm.
        colonies (List[Any]): A list of ant colony objects.
        prevCandSet (List[Any]): The previous candidate set.
        bestSoFar (List[Any]): The best solution found so far.
        iterNum (int): The current iteration number.
        candSetsPerIter (List[List[Any]]): A list of candidate sets for each iteration.
        jointFun (Callable): The joint objective function.

    Methods:
        initialize_colonies: Initializes the ant colonies.
        initialize_prev_cand_set: Initializes the previous candidate set.
        optimize: Optimizes the team composition.
        should_continue: Checks if the optimization should continue.
        iteration_step: Performs a single iteration step of the optimization.
        update_candidate_sets: Updates the candidate sets.
        getSolnTeamNames: Returns the names of the Pokemon in the best solution.
        getSoln: Returns the best solution as a Team object.
        getObjTeamValue: Returns the objective value of the best solution.
        plot_soln: Plots the values of the last cooperation candidate set.
        plot_iters: Plots the values of the candidate sets for each iteration.
        plot_averages: Plots the average values of the candidate sets for each iteration.
        plot_maxes: Plots the maximum values of the candidate sets for each iteration.
    """

    def __init__(
        self,
        total_population: int,
        objective_functions_Q_rho: list[Tuple[Callable, float, float]],
        pokemon_pop: list[Pokemon],
        preselected_pokemons: list[int],
        preselected_moves: list[list[int]],
        alpha: float,
        beta: float,
        cooperation_strategy: Callable = CooperationStats.SELECTION_BY_DOMINANCE,
        roles: list[str] = [],
    ):
        if total_population <= 0:
            raise ValueError("totalPopulation must be a positive integer")
        if alpha < 0 or beta < 0:
            raise ValueError("alpha and beta must be non-negative")

        self.total_population = total_population
        self.objective_functions_Q_rho = objective_functions_Q_rho
        self.cooperation_strategy = cooperation_strategy
        self.pokemon_pop = pokemon_pop
        self.preselected_pokemons = preselected_pokemons
        self.preSelected_moves = preselected_moves
        self.alpha = alpha
        self.beta = beta
        self.roles = roles
        self.colonies = self.initialize_colonies()
        self.prev_candidate_set = self.initialize_prev_cand_set()
        self.best_so_far = self.prev_candidate_set[0]
        self.iteration_number = 1
        self.candidate_sets_per_iteration = [self.prev_candidate_set]
        self.joint_function = lambda team: reduce(
            lambda acc, f: acc * f(team),
            [
                objective_function[0]
                for objective_function in self.objective_functions_Q_rho
            ],
            1,
        )

    def initialize_colonies(self):
        """
        Initializes the ant colonies.

        Returns:
            List[Any]: A list of ant colony objects.
        """
        return [
            Colony(
                int(self.total_population / len(self.objective_functions_Q_rho)),
                objFunc,
                self.pokemon_pop,
                self.preselected_pokemons,
                self.preSelected_moves,
                self.alpha,
                self.beta,
                Q,
                rho,
                self.roles,
            )
            for objFunc, Q, rho in self.objective_functions_Q_rho
        ]

    def initialize_prev_cand_set(self):
        """
        Initializes the previous candidate set.

        Returns:
            List[Any]: The previous candidate set.
        """
        cooperative_candidate_set = deepcopy(
            dominated_candidate_set(
                [colony.candidate_set() for colony in self.colonies],
                [objFunc[0] for objFunc in self.objective_functions_Q_rho],
            )
        )
        return cooperative_candidate_set

    def optimize(self, iters: int = None, time_limit: float = None):
        """
        Optimizes the team composition.

        Args:
            iters (int, optional): The maximum number of iterations. Defaults to None.
            time_limit (float, optional): The maximum time limit in seconds. Defaults to None.

        Raises:
            Exception: If neither iters nor time_limit is provided.
        """
        if iters is None and time_limit is None:
            raise Exception("Provide Termination Criteria")
        start_time = time.time()
        while self.should_continue(iters, time_limit, start_time):
            self.iteration_step()

    def should_continue(self, iters, time_limit, start_time):
        """
        Checks if the optimization should continue.

        Args:
            iters (int): The maximum number of iterations.
            time_limit (float): The maximum time limit in seconds.
            start_time (float): The start time of the optimization.

        Returns:
            bool: True if the optimization should continue, False otherwise.
        """
        return (iters is None or self.iteration_number < iters) and (
            time_limit is None or (time.time() - start_time) < time_limit
        )

    def iteration_step(self):
        """
        Performs a single iteration step of the optimization.
        """
        self.iteration_number += 1
        cooperation_function = self.cooperation_strategy
        self.colonies = cooperation_function(
            self.colonies, self.prev_candidate_set)
        self.update_candidate_sets()

    def update_candidate_sets(self):
        """
        Updates the candidate sets.
        """
        current_candidate_set = deepcopy(
            dominated_candidate_set(
                [colony.candidate_set() for colony in self.colonies],
                [objFunc[0] for objFunc in self.objective_functions_Q_rho],
            )
        )
        self.prev_candidate_set = deepcopy(
            dominated_candidate_set(
                [self.prev_candidate_set, current_candidate_set],
                [objFunc[0] for objFunc in self.objective_functions_Q_rho],
            )
        )
        self.candidate_sets_per_iteration.append(self.prev_candidate_set)
        iteration_best = self.prev_candidate_set[0]
        self.best_so_far = max(
            [iteration_best, self.best_so_far], key=self.joint_function
        )

    def get_solution_team_names(self):
        """
        Returns the names of the Pokemon in the best solution.

        Returns:
            List[str]: A list of Pokemon names.

        Raises:
            Exception: If the optimization has not been run.
        """
        team = []
        if self.best_so_far is not None:
            for pok in self.best_so_far:
                team += [self.pokemon_pop[pok[0]].name]
            return team
        else:
            raise Exception("Optimization has not been run.")

    def get_solution(self):
        """
        Returns the best solution as a Team object.

        Returns:
            Team: The best solution as a Team object.

        Raises:
            Exception: If the optimization has not been run.
        """
        team = Team()
        if self.best_so_far is not None:
            for pok in self.best_so_far:
                temp_pokemon = Pokemon.from_json(
                    self.pokemon_pop[pok[0]].serialize())
                for move_index in pok[1:]:
                    temp_pokemon.teach_move(move_index)
                team.add_pokemon(temp_pokemon)
            return team
        else:
            raise Exception("Optimization has not been run.")

    def get_objective_value(self):
        """
        Returns the objective value of the best solution.

        Returns:
            float: The objective value of the best solution.

        Raises:
            Exception: If the optimization has not been run.
        """
        if self.best_so_far is not None:
            return self.joint_function(self.best_so_far)
        else:
            raise Exception("Optimization has not been run.")

    def plot_soln(self, sorted_iterations):
        """
        Plots the values of the last cooperation candidate set.

        Args:
            sortedIters (bool): Whether to sort the values or not.

        Returns:
            go.Figure: The plotly figure object.
        """
        if sorted_iterations:
            a = sorted(list(map(self.joint_function, self.best_so_far)))
        else:
            a = list(map(self.joint_function, self.best_so_far))
        b = np.array(a)
        fig = go.Figure
        fig.add_trace(
            go.Scatter(
                x=range(0, b.size),
                y=b,
                mode="lines",
                name=f"Last Cand Set Team Values: Iter: {str(self.iteration_number)} - rho: {str(self.rho)} - Q: {str(self.Q)}",
            )
        )
        return fig

    def plot_iters(self, sorted_iterations):
        """
        Plots the values of the candidate sets for each iteration.

        Args:
            sortedIters (bool): Whether to sort the values or not.

        Returns:
            go.Figure: The plotly figure object.
        """
        sorted_df = pd.DataFrame(
            [
                sorted(list(map(self.joint_function, iteration_points[0])))
                for i, iteration_points in enumerate(self.candidate_sets_per_iteration)
            ]
        )
        unsorted_df = pd.DataFrame(
            [
                list(map(self.joint_function, iteration_points[0]))
                for i, iteration_points in enumerate(self.candidate_sets_per_iteration)
            ]
        )

        fig = go.Figure()
        if sorted_iterations:
            df = sorted_df
        else:
            df = unsorted_df
        for i in range(len(df)):
            fig.add_trace(
                go.Scatter(
                    x=df.columns, y=df.iloc[i, :], mode="lines", name=f"Iteration {i}"
                )
            )

        fig.update_layout(
            xaxis_title="Element Number",
            yaxis_title="Value",
            title=f"Line Plot for Each Iteration. Params alpha:{alpha}, beta: {beta}, Q: {Q}, rho: {rho}",
        )

        return fig

    def plot_averages(self):
        """
        Plots the average values of the candidate sets for each iteration.

        Returns:
            go.Figure: The plotly figure object.
        """
        averages = [
            np.mean(list(map(self.joint_function, iteration_points[0])))
            for iteration_points in self.candidate_sets_per_iteration
        ]

        fig = px.line(
            x=np.arange(len(averages)),
            y=averages,
            markers=True,
            line_shape="linear",
            labels={"y": "Average Y-axis Value"},
        )

        fig.update_layout(xaxis_title="Iteration",
                          yaxis_title="Average Y-axis Value")

        return fig

    def plot_maxes(self, fig=None):
        """
        Plots the maximum values of the candidate sets for each iteration.

        Args:
            fig (go.Figure, optional): The plotly figure object. Defaults to None.

        Returns:
            go.Figure: The plotly figure object.
        """
        averages = [
            self.joint_function(iteration_points[0][0])
            for iteration_points in self.candidate_sets_per_iteration
        ]

        fig = px.line(
            x=np.arange(len(averages)),
            y=averages,
            markers=True,
            line_shape="linear",
            labels={"y": "Average Y-axis Value"},
        )

        fig.update_layout(xaxis_title="Iteration",
                          yaxis_title="Average Y-axis Value")

        return fig
