from functools import wraps
from typing import Any, Callable, Iterable

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

    def optimize(self, pop_size: int, n_gen: int, verbose: bool, history: bool = False) -> None:
        algorithm = NSGA2(
            pop_size=pop_size,
            sampling=PokemonTeamSampling(random_state=self.random_state),
            crossover=PokemonCrossover(prob_pokemon=0.5, random_state=self.random_state),
            mutation=PokemonMutation(prob_pokemon=0.5, prob_move=0.5, random_state=self.random_state),
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
        return res

    def has_been_optimized() -> Callable[..., Any]:
        def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
            @wraps(func)
            def wrapper(self: "PokeTactician", *args, **kwargs) -> Callable[..., Any]:
                if self.results is None:
                    raise ValueError("No results available. Run optimize() first.")
                return func(self, *args, **kwargs)

            return wrapper

        return decorator

    def with_history() -> Callable[..., Any]:
        def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
            @wraps(func)
            def wrapper(self: "PokeTactician", *args, **kwargs) -> Callable[..., Any]:
                if not self.results.algorithm.save_history:
                    raise ValueError("History is not saved. Set save_history=True in optimize().")
                return func(self, *args, **kwargs)

            return wrapper

        return decorator

    @has_been_optimized()
    def solutions_plot(self) -> None:
        import matplotlib.pyplot as plt

        F = self.results.F
        if F.shape[1] != 2:
            raise ValueError("This method only supports 2 objectives for plotting.")
        plt.figure(figsize=(7, 5))
        plt.scatter(F[:, 0], F[:, 1], s=30, facecolors="none", edgecolors="blue")
        plt.title("Objective Space")
        plt.show()

    @has_been_optimized()
    @with_history()
    def convergence_plot(self) -> None:
        import matplotlib.pyplot as plt

        n_evals = np.array([e.evaluator.n_eval for e in self.results.history])

        opt = np.array([e.opt[0].F for e in self.results.history])

        plt.title("Convergence")
        plt.plot(n_evals, abs(opt), "--")
        plt.show()

    @has_been_optimized()
    @with_history()
    def running_metric_plot(self) -> None:
        from pymoo.util.running_metric import RunningMetricAnimation

        running = RunningMetricAnimation(delta_gen=10, n_plots=10, key_press=False, do_show=True)
        for algorithm in self.results.history:
            running.update(algorithm)
