from typing import Collection, cast

import numpy as np
from numpy.typing import NDArray
from pymoo.algorithms.moo.nsga2 import NSGA2
from pymoo.core.result import Result
from pymoo.optimize import minimize
from pymoo.termination import get_termination

import poketactician.objectives  # noqa: F401 — triggers objective registration
from poketactician.engine.crossover import PokemonCrossover
from poketactician.engine.mutation import PokemonMutation
from poketactician.engine.problem import PokemonProblem
from poketactician.engine.sampling import PokemonTeamSampling
from poketactician.engine.selector import ObjectiveSelector
from poketactician.registry import register_objective_data
from poketactician.utils import DecisionFunction, ResultsWithHistory, StrictResults


class PokeTactician:
    def __init__(
        self,
        objectives: Collection[str],
        seed: int | None,
        learnable_moves: NDArray[np.bool_],
        moves_category: NDArray[np.int16],
        pokemon_types: NDArray[np.bool_],
        move_types: NDArray[np.bool_],
        pokemon_stats: NDArray[np.int16],
        natures: NDArray[np.int16] | None = None,
        pre_selected: dict | None = None,
        n_pokemon: int = 6,
        decision_function: DecisionFunction | None = None,
        decision_function_kwargs: dict | None = None,
    ) -> None:
        self.learnable_moves = learnable_moves
        self.seed = seed
        self.moves_category = moves_category
        self.pokemon_types = pokemon_types
        self.move_types = move_types
        self.pokemon_stats = pokemon_stats
        self.n_pokemon = n_pokemon
        self.natures = natures if natures is not None else np.ones((25, 6), dtype=np.int16)
        self.n_moves = learnable_moves.shape[1]
        self.n_types = pokemon_types.shape[1]
        self._decision_function = decision_function if decision_function is not None else None
        self._decision_function_kwargs = decision_function_kwargs if decision_function_kwargs is not None else {}
        self.pre_selected = pre_selected if pre_selected else None
        self._results: Result | StrictResults | None = None
        data_context = {
            "learnable_moves": self.learnable_moves,
            "moves_category": self.moves_category,
            "pokemon_types": self.pokemon_types,
            "move_types": self.move_types,
            "pokemon_stats": self.pokemon_stats,
            "natures": self.natures,
        }
        register_objective_data(data_context, objective_names=objectives)
        self.objectives = ObjectiveSelector(objective_names=objectives)
        self.random_state = np.random.default_rng(seed) if seed is not None else np.random.default_rng()
        self.problem = PokemonProblem(
            objectives=self.objectives,
            lm=self.learnable_moves,
            n_pokemon=self.n_pokemon,
            n_moves=self.n_moves,
            pokemon_in_team=min(self.n_pokemon, 6),
        )

    def optimize(self, pop_size: int, n_gen: int, verbose: bool, history: bool = False) -> StrictResults:
        algorithm = NSGA2(
            pop_size=pop_size,
            sampling=PokemonTeamSampling(random_state=self.random_state, pre_selected=self.pre_selected),  # type: ignore
            crossover=PokemonCrossover(prob_pokemon=0.5, random_state=self.random_state),  # type: ignore
            mutation=PokemonMutation(
                prob_pokemon=0.5,
                prob_move=0.5,
                random_state=self.random_state,
                pre_selected=self.pre_selected if self.pre_selected is not None else None,
            ),  # type: ignore
            eliminate_duplicates=True,
        )

        termination = get_termination("n_gen", n_gen)
        res = cast(
            StrictResults,
            minimize(
                problem=self.problem,
                algorithm=algorithm,
                termination=termination,
                seed=self.seed,
                verbose=verbose,
                save_history=history,
            ),
        )
        if len(res.X.shape) == 1:
            res.X = np.atleast_2d(res.X)
            res.F = np.atleast_2d(res.F)
        self._results = res
        return cast(StrictResults, res)

    @property
    def results(self) -> StrictResults:
        if self._results is None:
            raise ValueError("No results available. Run optimize() first.")
        return cast(StrictResults, self._results)

    def decision_function(self) -> NDArray[np.int16]:
        """
        Computes and returns the decision function values as a NumPy array of type int16 on the Pareto Set.
        If a custom decision function is defined (`self._decision_function`), it is applied to the input data (`self.results.X`).
        Otherwise, the input data is converted to at least 2D and the first row is returned.
        Returns:
            NDArray[np.int16]: The computed decision function values.
        """

        if self._decision_function is not None:
            result = self._decision_function(self.results.X, **self._decision_function_kwargs)
        else:
            result = np.atleast_2d(self.results.X)[0]
        return result

    @property
    def best_solution(self) -> NDArray[np.int16]:
        return self.decision_function()

    @property
    def _history_results(self) -> ResultsWithHistory:
        res = self.results
        # Note: Depending on your library, ensure 'algorithm' and 'save_history' are typed correctly
        if hasattr(res.algorithm, "save_history") and not res.algorithm.save_history:
            raise ValueError("History is not saved. Set save_history=True in optimize().")
        return cast(ResultsWithHistory, res)

    def solutions_plot(self) -> None:
        import matplotlib.pyplot as plt

        F = self.results.F
        if len(F.shape) < 2 or F.shape[1] != 2:
            raise ValueError("This method only supports 2 objectives for plotting.")
        plt.figure(figsize=(7, 5))
        plt.scatter(F[:, 0], F[:, 1], s=30, facecolors="none", edgecolors="blue")
        plt.title("Objective Space")
        plt.show()

    def convergence_plot(self) -> None:
        import matplotlib.pyplot as plt

        result: ResultsWithHistory = self._history_results

        n_evals = np.array([e.evaluator.n_eval for e in result.history])

        opt = np.array([e.opt[0].F for e in result.history])
        plt.title("Convergence")
        plt.plot(n_evals, abs(opt), "--")
        plt.show()

    def running_metric_plot(self) -> None:
        from pymoo.util.running_metric import RunningMetricAnimation

        result: ResultsWithHistory = self._history_results
        running = RunningMetricAnimation(delta_gen=10, n_plots=10, key_press=False, do_show=True)
        for algorithm in result.history:
            running.update(algorithm)
