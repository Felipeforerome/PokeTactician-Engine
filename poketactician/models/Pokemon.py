from .Move import Move


class Pokemon:
    def __init__(self, id, name, hp, att, deff, spatt, spdeff, spe, type1, type2):
        self.id = id
        self.name = name
        self.hp = hp
        self.att = att
        self.deff = deff
        self.spatt = spatt
        self.spdeff = spdeff
        self.spe = spe
        self.knowableMoves = []
        self.learntMoves = []
        self.type1 = type1
        self.type2 = type2

    def addKnowableMove(self, move):
        """
        TODO This should be changed once more info about the moves is added, like effects or whatever. Right now it does reduce the decision space
        Adds move to list of knowable move if it has power greater to 0, its between the best 3 moves wtht that type and class
        :param move: Move to add
        """
        sameTypeClass = False
        sameTypeClassMoves = []
        numTypeClass = 0
        if move.power == 0:
            return

        for knownMove in self.knowableMoves:
            diffType = knownMove.type != move.type
            diffClass = knownMove.damageClass != move.damageClass
            if diffType or diffClass:
                continue
            else:
                numTypeClass = numTypeClass + 1
                sameTypeClassMoves.append(knownMove)
                lenTypeClassMoves = sameTypeClassMoves.__len__()

                if lenTypeClassMoves == 3:
                    sameTypeClass = True
                    sameTypeClassMoves.sort(key=lambda x: x.power * x.accuracy)
                    for knownTypeClass in sameTypeClassMoves:
                        increasedPowerAccuracy = (
                            knownTypeClass.power * knownTypeClass.accuracy
                            <= move.power * move.accuracy
                        )
                        increasedPP = knownMove.pp * 0.75 <= move.pp

                        if increasedPowerAccuracy:
                            if increasedPP or knownTypeClass.power + 30 <= move.power:
                                self.knowableMoves.remove(knownTypeClass)
                                self.knowableMoves.append(move)
                                return
                        else:
                            return

        if not sameTypeClass:
            self.knowableMoves.append(move)

    @staticmethod
    def from_json(data):
        pokemon = Pokemon(
            data["id"],
            data["name"],
            data["hp"],
            data["att"],
            data["deff"],
            data["spatt"],
            data["spdeff"],
            data["spe"],
            data["type1"],
            data["type2"],
        )
        moves = [Move.from_json(move_data) for move_data in data["knowableMoves"]]

        for move in moves:
            pokemon.addKnowableMove(move)
        return pokemon

    def serialize(pokemon):
        serialized_moves = [move.serialize() for move in pokemon.knowableMoves]
        return {
            "id": pokemon.id,
            "name": pokemon.name,
            "hp": pokemon.hp,
            "att": pokemon.att,
            "deff": pokemon.deff,
            "spatt": pokemon.spatt,
            "spdeff": pokemon.spdeff,
            "spe": pokemon.spe,
            "type1": pokemon.type1,
            "type2": pokemon.type2,
            "knowableMoves": serialized_moves,
        }

    def serialize_instance(self):
        serialized_moves = [move.serialize() for move in self.learntMoves]
        return {
            "id": self.id,
            "name": self.name,
            "hp": self.hp,
            "att": self.att,
            "deff": self.deff,
            "spatt": self.spatt,
            "spdeff": self.spdeff,
            "spe": self.spe,
            "type1": self.type1,
            "type2": self.type2,
            "moves": serialized_moves,
        }

    def teachMove(self, int):
        self.learntMoves += [self.knowableMoves[int]]

    def overallStats(self):
        """
        Calculates the sum of stats
        :return: Sum of Stats
        """
        return self.hp + self.att + self.deff + self.spatt + self.spdeff + self.spe
