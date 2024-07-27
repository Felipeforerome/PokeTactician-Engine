from .Colony import Colony


def selectionByDominance(colonies: list[Colony], prevCandSet):
    for colony in colonies:
        colony.update_ph_concentration(prevCandSet)
        colony.update_pokemon_prob()
        colony.ACO()
    return colonies
