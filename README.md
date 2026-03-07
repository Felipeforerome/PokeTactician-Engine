# PokeTactician Engine

Multi-Objective Evolutionary Algorithm implementation for team building in Pokemon.

## General Info

This optimizer is built on the pymoo framework to build a team for Pokemon following multiple objectives. The objectives can include:
* Maximize expected damage of the team
* Maximize type coverage for the team
* Custom objectives defined by the user

Besides this, certain constraints can be added to the problem definition:
* Subset of pokemon to use to build the team
* Learnable moves for each Pokemon
* Number of Pokemon in the team
* Whether Pokemon can be repeated in the team

## Technologies

The algorithm used is NSGA-II (Non-dominated Sorting Genetic Algorithm II), a popular multi-objective evolutionary algorithm. The implementation leverages the pymoo framework for the core optimization components.

Everything is built using Python with libraries like numpy, pymoo, and matplotlib for visualization. The project is designed to be modular and extensible, allowing for easy addition of new objectives and constraints.

## Installation

To install the package, run:

```bash
pip install -e .
```

## Testing

The project includes a comprehensive test suite covering all major components. To run the tests:

```bash
# Run all tests
python run_tests.py

# Run specific test files
pytest tests/engine/test_problem.py
pytest tests/test_poketactician.py

# Run tests with coverage report
pytest --cov=poketactician --cov-report=term-missing
```

## Usage

Basic usage example:

```python
from poketactician.poketactician import PokeTactician

# Initialize data matrices
# lm: Learnable Moves matrix (Pokemon x Moves)
# me: Move Effectiveness matrix
# pt: Pokemon Types matrix
# mt: Move Types matrix
# ps: Pokemon Stats matrix

# Create a PokeTactician instance
tactician = PokeTactician(
    objectives=["test_objective", "test_objective2"],
    seed=42,
    lm=lm,
    me=me,
    pt=pt,
    mt=mt,
    ps=ps,
    n_pokemon=6
)

# Run optimization
result = tactician.optimize(pop_size=100, n_gen=50, verbose=True, history=True)

# Visualize results
tactician.solutions_plot()
tactician.convergence_plot()
```

## Project Structure

```
poketactician/
├── __init__.py
├── config.py
├── poketactician.py     # Main class
├── registry.py          # Objective registry
├── utils.py             # Utility functions
├── engine/              # Optimization engine components
│   ├── crossover.py     # Pokemon team crossover
│   ├── mutation.py      # Pokemon team mutation
│   ├── problem.py       # Problem definition
│   ├── sampling.py      # Initial population sampling
│   └── selector.py      # Objective selector
└── objectives/          # Objective functions
    └── test_objectives.py

tests/                   # Test suite
├── conftest.py          # Test fixtures
├── test_poketactician.py
├── test_registry.py
├── test_utils.py
├── engine/
│   ├── test_crossover.py
│   ├── test_mutation.py
│   ├── test_problem.py
│   ├── test_sampling.py
│   └── test_selector.py
└── objectives/
    └── test_objective_functions.py
```
