import time
import numpy as np
from copy import deepcopy
from functools import reduce
from .utils import (
    dominatedCandSet,
)
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
from .glob_var import cooperationStatsDict, alpha, beta, Q, rho


###Multi Objective Ant Colony Optimization Algorithm
class MOACO:
    def __init__(
        self,
        colonyClass,
        totalPopulation,
        objFuncs_Q_rho,
        pokemonPop,
        alpha,
        beta,
        cooperationID=1,
    ):
        self.totalPopulation = totalPopulation
        self.objFuncs_Q_rho = objFuncs_Q_rho
        self.cooperationID = cooperationID
        self.pokemonPop = pokemonPop
        self.prevCandSet = None
        self.iterNum = 1
        self.plot = None
        self.candSetsPerIter = []
        self.alpha = alpha
        self.beta = beta
        self.Q = Q
        self.rho = rho
        self.jointFun = lambda team: reduce(
            lambda acc, f: acc * f(team),
            [objFunc[0] for objFunc in self.objFuncs_Q_rho],
            1,
        )
        # Initialize Colonies
        self.colonies = [
            colonyClass(
                int(self.totalPopulation / len(self.objFuncs_Q_rho)),
                objFunc,
                self.pokemonPop,
                self.alpha,
                self.beta,
                Q,
                rho,
            )
            for objFunc, Q, rho in self.objFuncs_Q_rho
        ]

        coopCandSet = deepcopy(
            dominatedCandSet(
                [colony.candidateSet() for colony in self.colonies],
                [objFunc[0] for objFunc in self.objFuncs_Q_rho],
            )
        )

        self.prevCandSet = coopCandSet
        self.candSetsPerIter.append([self.prevCandSet])
        self.bestSoFar = self.prevCandSet[0]

    def optimize(self, iters=None, time_limit=None):
        if iters == None and time_limit == None:
            raise Exception("Provide Termination Criteria")
        colonies = self.colonies
        start_time = time.time()
        while (iters is None or self.iterNum < iters) and (
            time_limit is None or (time.time() - start_time) < time_limit
        ):
            self.iterNum += 1
            coopStratFun = cooperationStatsDict[self.cooperationID]
            colonies = coopStratFun(colonies, self.prevCandSet)
            currentCandSet = deepcopy(
                dominatedCandSet(
                    [colony.candidateSet() for colony in colonies],
                    [objFunc[0] for objFunc in self.objFuncs_Q_rho],
                )
            )
            self.prevCandSet = deepcopy(
                dominatedCandSet(
                    [self.prevCandSet, currentCandSet],
                    [objFunc[0] for objFunc in self.objFuncs_Q_rho],
                )
            )
            self.candSetsPerIter.append([self.prevCandSet])
            iterationBest = self.prevCandSet[0]
            self.bestSoFar = max([iterationBest, self.bestSoFar], key=self.jointFun)

    def getSolnTeamNames(self):
        team = []
        if self.bestSoFar is not None:
            for pok in self.bestSoFar:
                team += [self.pokemonPop[pok[0]].name]
            return team
        else:
            raise Exception("Optimization has not been ran.")

    def getObjTeamValue(self):
        if self.bestSoFar is not None:
            return self.jointFun(self.bestSoFar)
        else:
            raise Exception("Optimization has not been ran.")

    def plot_soln(self, sortedIters):
        # This plot shows the last cooperation candidate set values
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
        # Plot iteration points
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

        # Assuming df is your DataFrame with columns 0 to 29
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
        # Plot averages
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

        # Add labels and legend
        fig.update_layout(xaxis_title="Iteration", yaxis_title="Average Y-axis Value")

        # Show the plot
        return fig

    def plot_maxes(self, fig=None):
        # Plot averages
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

        # Add labels and legend
        fig.update_layout(xaxis_title="Iteration", yaxis_title="Average Y-axis Value")

        # Show the plot
        return fig
