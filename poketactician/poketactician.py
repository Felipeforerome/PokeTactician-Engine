from typing import Iterable, cast

import numpy as np
from numpy.typing import NDArray
from pymoo.algorithms.moo.nsga2 import NSGA2
from pymoo.core.result import Result
from pymoo.optimize import minimize
from pymoo.termination import get_termination

from poketactician.engine.crossover import PokemonCrossover
from poketactician.engine.mutation import PokemonMutation
from poketactician.engine.problem import PokemonProblem
from poketactician.engine.sampling import PokemonTeamSampling
from poketactician.engine.selector import ObjectiveSelector
from poketactician.objectives.dummy_objectives import test_objective, test_objective2  # noqa: F401
from poketactician.registry import register_objective_data
from poketactician.utils import ResultsWithHistory, StrictResults


class PokeTactician:
    def __init__(
        self,
        objectives: Iterable[str],
        seed: int | None,
        lm: NDArray[np.bool_],
        me: NDArray[np.int16],
        pt: NDArray[np.bool_],
        mt: NDArray[np.bool_],
        ps: NDArray[np.int16],
        pre_selected: Iterable[int] | NDArray[np.int16] | None = None,
        n_pokemon: int = 6,
    ) -> None:
        self.lm = lm
        self.seed = seed
        self.me = me
        self.pt = pt
        self.mt = mt
        self.ps = ps
        self.n_pokemon = n_pokemon
        self.n_moves = lm.shape[1]
        self.n_types = pt.shape[1]
        if pre_selected is None:
            self.pre_selected = None
        # elif isinstance(pre_selected, np.ndarray):
        #     self.pre_selected = pre_selected.astype(np.int16)
        else:
            self.pre_selected = np.array(list(pre_selected), dtype=np.int16)
        self.results: Result | None = None
        register_objective_data(
            {
                "test_objective": {"me": self.me},
                "test_objective2": {"me": self.me},
            }
        )
        self.objectives = ObjectiveSelector(objectives)
        self.random_state = np.random.default_rng(seed) if seed is not None else np.random.default_rng()
        self.problem = PokemonProblem(
            objectives=self.objectives, lm=self.lm, n_pokemon=self.n_pokemon, n_moves=self.n_moves, pokemon_in_team=min(self.n_pokemon, 6)
        )

    def optimize(self, pop_size: int, n_gen: int, verbose: bool, history: bool = False) -> StrictResults:
        algorithm = NSGA2(
            pop_size=pop_size,
            sampling=PokemonTeamSampling(random_state=self.random_state, pre_selected=self.pre_selected),
            crossover=PokemonCrossover(prob_pokemon=0.5, random_state=self.random_state),
            mutation=PokemonMutation(prob_pokemon=0.5, prob_move=0.5, random_state=self.random_state, pre_selected=self.pre_selected),
            eliminate_duplicates=True,
        )

        termination = get_termination("n_gen", n_gen)
        res = minimize(
            problem=self.problem,
            algorithm=algorithm,
            termination=termination,
            seed=self.seed,
            verbose=verbose,
            save_history=history,
        )
        self.results = res
        return cast(StrictResults, res)

    @property
    def _safe_results(self) -> StrictResults:
        if self.results is None:
            raise ValueError("No results available. Run optimize() first.")
        return cast(StrictResults, self.results)

    @property
    def _history_results(self) -> ResultsWithHistory:
        res = self._safe_results
        # Note: Depending on your library, ensure 'algorithm' and 'save_history' are typed correctly
        if hasattr(res.algorithm, "save_history") and not res.algorithm.save_history:
            raise ValueError("History is not saved. Set save_history=True in optimize().")
        return cast(ResultsWithHistory, res)

    def solutions_plot(self) -> None:
        import matplotlib.pyplot as plt

        F = self._safe_results.F
        if F.shape[1] != 2:
            raise ValueError("This method only supports 2 objectives for plotting.")
        plt.figure(figsize=(7, 5))
        plt.scatter(F[:, 0], F[:, 1], s=30, facecolors="none", edgecolors="blue")
        plt.title("Objective Space")
        plt.show()

    def convergence_plot(self) -> None:
        import matplotlib.pyplot as plt

        result = self._history_results

        n_evals = np.array([e.evaluator.n_eval for e in result.history])

        opt = np.array([e.opt[0].F for e in result.history])
        plt.title("Convergence")
        plt.plot(n_evals, abs(opt), "--")
        plt.show()

    def running_metric_plot(self) -> None:
        from pymoo.util.running_metric import RunningMetricAnimation

        result = self._history_results
        running = RunningMetricAnimation(delta_gen=10, n_plots=10, key_press=False, do_show=True)
        for algorithm in result.history:
            running.update(algorithm)
