def selectionByDominance(colonies, prevCandSet):
    for colony in colonies:
        colony.updatePhCon(prevCandSet)
        colony.updatePokProb()
        colony.ACO()
    return colonies
