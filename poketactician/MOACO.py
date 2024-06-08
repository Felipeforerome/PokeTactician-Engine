import time
from copy import deepcopy
from functools import reduce
from typing import Any, Callable, List, Tuple

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from .Colony import Colony
from .glob_var import Q, alpha, beta, cooperationStatsDict, rho
from .models.Team import Team
from .utils import dominatedCandSet


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
        cooperationID (int, optional): The ID of the cooperation strategy to use. Defaults to 1.

    Raises:
        ValueError: If totalPopulation is not a positive integer or if alpha or beta are negative.

    Attributes:
        totalPopulation (int): The total population size.
        objFuncs_Q_rho (List[Tuple[Callable, float, float]]): A list of tuples containing the objective functions,
            pheromone decay rate (Q), and pheromone evaporation rate (rho).
        cooperationID (int): The ID of the cooperation strategy used.
        pokemonPop (List[Any]): A list of Pokemon objects representing the available Pokemon population.
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
        totalPopulation: int,
        objFuncs_Q_rho: List[Tuple[Callable, float, float]],
        pokemonPop: List[Any],
        preSelected: List[int],
        alpha: float,
        beta: float,
        cooperationID: int = 1,
    ):
        if totalPopulation <= 0:
            raise ValueError("totalPopulation must be a positive integer")
        if alpha < 0 or beta < 0:
            raise ValueError("alpha and beta must be non-negative")

        self.totalPopulation = totalPopulation
        self.objFuncs_Q_rho = objFuncs_Q_rho
        self.cooperationID = cooperationID
        self.pokemonPop = deepcopy(pokemonPop)
        self.preSelected = preSelected
        self.alpha = alpha
        self.beta = beta
        self.colonies = self.initialize_colonies()
        self.prevCandSet = self.initialize_prev_cand_set()
        self.bestSoFar = self.prevCandSet[0]
        self.iterNum = 1
        self.candSetsPerIter = [self.prevCandSet]
        self.jointFun = lambda team: reduce(
            lambda acc, f: acc * f(team),
            [objFunc[0] for objFunc in self.objFuncs_Q_rho],
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
                int(self.totalPopulation / len(self.objFuncs_Q_rho)),
                objFunc,
                self.pokemonPop,
                self.preSelected,
                self.alpha,
                self.beta,
                Q,
                rho,
            )
            for objFunc, Q, rho in self.objFuncs_Q_rho
        ]

    def initialize_prev_cand_set(self):
        """
        Initializes the previous candidate set.

        Returns:
            List[Any]: The previous candidate set.
        """
        coopCandSet = deepcopy(
            dominatedCandSet(
                [colony.candidateSet() for colony in self.colonies],
                [objFunc[0] for objFunc in self.objFuncs_Q_rho],
            )
        )
        return coopCandSet

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
        return (iters is None or self.iterNum < iters) and (
            time_limit is None or (time.time() - start_time) < time_limit
        )

    def iteration_step(self):
        """
        Performs a single iteration step of the optimization.
        """
        self.iterNum += 1
        coopStratFun = cooperationStatsDict[self.cooperationID]
        self.colonies = coopStratFun(self.colonies, self.prevCandSet)
        self.update_candidate_sets()

    def update_candidate_sets(self):
        """
        Updates the candidate sets.
        """
        currentCandSet = deepcopy(
            dominatedCandSet(
                [colony.candidateSet() for colony in self.colonies],
                [objFunc[0] for objFunc in self.objFuncs_Q_rho],
            )
        )
        self.prevCandSet = deepcopy(
            dominatedCandSet(
                [self.prevCandSet, currentCandSet],
                [objFunc[0] for objFunc in self.objFuncs_Q_rho],
            )
        )
        self.candSetsPerIter.append(self.prevCandSet)
        iterationBest = self.prevCandSet[0]
        self.bestSoFar = max([iterationBest, self.bestSoFar], key=self.jointFun)

    def getSolnTeamNames(self):
        """
        Returns the names of the Pokemon in the best solution.

        Returns:
            List[str]: A list of Pokemon names.

        Raises:
            Exception: If the optimization has not been run.
        """
        team = []
        if self.bestSoFar is not None:
            for pok in self.bestSoFar:
                team += [self.pokemonPop[pok[0]].name]
            return team
        else:
            raise Exception("Optimization has not been run.")

    def getSoln(self):
        """
        Returns the best solution as a Team object.

        Returns:
            Team: The best solution as a Team object.

        Raises:
            Exception: If the optimization has not been run.
        """
        team = Team()
        if self.bestSoFar is not None:
            for pok in self.bestSoFar:
                tempPokemon = deepcopy(self.pokemonPop[pok[0]])
                for move_index in pok[1:]:
                    tempPokemon.teachMove(move_index)
                team.addPokemon(tempPokemon)
            return team
        else:
            raise Exception("Optimization has not been run.")

    def getObjTeamValue(self):
        """
        Returns the objective value of the best solution.

        Returns:
            float: The objective value of the best solution.

        Raises:
            Exception: If the optimization has not been run.
        """
        if self.bestSoFar is not None:
            return self.jointFun(self.bestSoFar)
        else:
            raise Exception("Optimization has not been run.")

    def plot_soln(self, sortedIters):
        """
        Plots the values of the last cooperation candidate set.

        Args:
            sortedIters (bool): Whether to sort the values or not.

        Returns:
            go.Figure: The plotly figure object.
        """
        if sortedIters:
            a = sorted(list(map(self.jointFun, self.bestSoFar)))
        else:
            a = list(map(self.jointFun, self.bestSoFar))
        b = np.array(a)
        fig = go.Figure
        fig.add_trace(
            go.Scatter(
                x=range(0, b.size),
                y=b,
                mode="lines",
                name=f"Last Cand Set Team Values: Iter: {str(self.iterNum)} - rho: {str(self.rho)} - Q: {str(self.Q)}",
            )
        )
        return fig

    def plot_iters(self, sortedIters):
        """
        Plots the values of the candidate sets for each iteration.

        Args:
            sortedIters (bool): Whether to sort the values or not.

        Returns:
            go.Figure: The plotly figure object.
        """
        sortedDF = pd.DataFrame(
            [
                sorted(list(map(self.jointFun, iteration_points[0])))
                for i, iteration_points in enumerate(self.candSetsPerIter)
            ]
        )
        unsortedDF = pd.DataFrame(
            [
                list(map(self.jointFun, iteration_points[0]))
                for i, iteration_points in enumerate(self.candSetsPerIter)
            ]
        )

        fig = go.Figure()
        if sortedIters:
            df = sortedDF
        else:
            df = unsortedDF
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
            np.mean(list(map(self.jointFun, iteration_points[0])))
            for iteration_points in self.candSetsPerIter
        ]

        fig = px.line(
            x=np.arange(len(averages)),
            y=averages,
            markers=True,
            line_shape="linear",
            labels={"y": "Average Y-axis Value"},
        )

        fig.update_layout(xaxis_title="Iteration", yaxis_title="Average Y-axis Value")

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
            self.jointFun(iteration_points[0][0])
            for iteration_points in self.candSetsPerIter
        ]

        fig = px.line(
            x=np.arange(len(averages)),
            y=averages,
            markers=True,
            line_shape="linear",
            labels={"y": "Average Y-axis Value"},
        )

        fig.update_layout(xaxis_title="Iteration", yaxis_title="Average Y-axis Value")

        return fig
