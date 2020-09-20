#Pokemon Team Optimizer

Multi-Objective Ant Colony Optimizer implementation for team building in Pokemon

##General Info

This optimizer is build on MO-ACO to build a team for Pokemon following multiple objectives with different units each. The objectives are:
* Maximize type coverage of the team as a whole
* Maximize expected damage dealt per type
* Maximize coverage of each individual pokemon
* Maximize expected damage dealt, per pokemon


##Technologies

As stated before the algorithm used is MO-ACO, with multiple colonies, on per objective and respective objective function. These colonies collaborate through mixing of their respective candidate sets. It's further improved by using Local Search on the ants selected through the regular algorithm.

Everything is built using Python and libraries like numpy and random. A huge help came from the project pokebase. This allowed me to query a local database with all the raw data needed. This was further modified for the specific use of this project.

The implementation of the meta-heuristic is done manually as modifying current implementation would result in the same amount of work, and it was built as an exercise to comprehend the inner workings of this meta-heuristic.

##Features

Right now it will build a team only following one objective, building the collaboration mechanism should come in the near future.

###To-Do:

* Finish the collaboration mechanism.
* A user-friendly web interface, so it can be uploaded to a website for everyone to use.
* A filtering feature for the pokemon from which to build a team.