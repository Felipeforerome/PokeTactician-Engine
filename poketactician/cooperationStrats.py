from collections.abc import Iterable

from .Colony import Colony
from .models.hinting_types import Ant


def selectionByDominance(
    colonies: Iterable[Colony], prev_candidate_set: Iterable[Ant]
) -> Iterable[Colony]:
    for colony in colonies:
        # TODO I think the problem was actually here
        colony.update_ph_concentration(prev_candidate_set)
        colony.update_pokemon_prob()
        colony.ACO()
    return colonies
