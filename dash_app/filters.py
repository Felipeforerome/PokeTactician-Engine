def filterTypes(pokPreFilter, includedTypes, monoType):
    if len(includedTypes) > 0:
        pokList = (
            [
                pok
                for pok in pokPreFilter
                if (pok.type1 in includedTypes and pok.type2 is None)
            ]
            if monoType
            else [
                pok
                for pok in pokPreFilter
                if (pok.type1 in includedTypes or pok.type2 in includedTypes)
            ]
        )
    else:
        pokList = (
            [pok for pok in pokPreFilter if (pok.type2 is None)]
            if monoType
            else pokPreFilter
        )
    return pokList


# Function to check if an id is within any of the provided ranges
def filterGenerations(pokPreFilter, gens):
    def is_id_in_range(id, ranges):
        for start, end in ranges:
            if start <= id <= end:
                return True
        return False

    pokList = []
    if len(gens) < 1:
        pokList = pokPreFilter
    else:
        pokList = [obj for obj in pokPreFilter if is_id_in_range(obj.id, gens)]

    return pokList
