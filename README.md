# Pokemon Team Optimizer

Multi-Objective Ant Colony Optimizer implementation for team building in Pokemon

## General Info

This optimizer is build on MO-ACO to build a team for Pokemon following multiple objectives with different units each. The objectives are:
* Maximize expected damage of the team
* Maxime type coverage for the team

Besides this, certain contrains can be added to the problem definition:
* Subset of pokemon to use to build the team
* Preselect pokemon with attacks that should be in the team
* Strategy of the team (Generalist, Offensive, or Defensive)
* Pokemon Roles that must be present in the team


## Technologies

As stated before the algorithm used is MO-ACO, with multiple colonies, one per objective and respective objective function. The algorithm can leverage different cooperations strategies between the colonies to obtain the optimzal output taking all objectives into account, though only one strategie has been implemented so far.

Everything is built using Python using libraries like numpy, dash-plotly, among others. A huge help came from the project pokebase, as it is used as a base for the pokemon that are going to be used in the algorithm. It has been further enhanced with meta data from other sources to enable different types of filtering.

The nature of this project has been as a sandbox where I try out libraries, methods, paradigms, etc. that I find interesting and want to learn.
