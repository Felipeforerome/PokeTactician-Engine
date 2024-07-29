from .Colony import Colony


def selectionByDominance(colonies: list[Colony], prev_candidate_set):
    for colony in colonies:
        colony.update_ph_concentration(prev_candidate_set)
        colony.update_pokemon_prob()
        colony.ACO()
    return colonies
