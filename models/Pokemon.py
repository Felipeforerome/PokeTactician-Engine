class Pokemon:
    def __init__(self, name, hp, att, deff, spatt, spdeff, spe, type1, type2):
        self.name = name
        self.hp = hp
        self.att = att
        self.deff = deff
        self.spatt = spatt
        self.spdeff = spdeff
        self.spe = spe
        self.knowableMoves = []
        self.type1 = type1
        self.type2 = type2

    def addKnowableMove(self, move):
        """
        Adds move to list of knowable move if it has power greater to 0, its between the best 3 moves wtht that type and class
        :param move: Move to add
        """
        sameTypeClass = False
        sameTypeClassMoves = []
        numTypeClass = 0
        if(move.power == 0):
            return

        for knownMove in self.knowableMoves:
            diffType = knownMove.type != move.type
            diffClass = knownMove.damageClass != move.damageClass
            if(diffType or diffClass):
                continue
            else:
                numTypeClass = numTypeClass + 1
                sameTypeClassMoves.append(knownMove)
                lenTypeClassMoves = sameTypeClassMoves.__len__()

                if(lenTypeClassMoves == 3 ):
                    sameTypeClass = True
                    sameTypeClassMoves.sort(key= lambda x: x.power*x.accuracy)
                    for knownTypeClass in sameTypeClassMoves:
                        increasedPowerAccuracy = knownTypeClass.power * knownTypeClass.accuracy <= move.power * move.accuracy
                        increasedPP = knownMove.pp*0.75 <= move.pp

                        if(increasedPowerAccuracy):
                            if(increasedPP or knownTypeClass.power+30<=move.power):
                                self.knowableMoves.remove(knownTypeClass)
                                self.knowableMoves.append(move)
                                return
                        else:
                            return

        if(not sameTypeClass):
            self.knowableMoves.append(move)


    def overallStats(self):
        """
        Calculates the sum of stats
        :return: Sum of Stats
        """
        return (self.hp + self.att + self.deff + self.spatt + self.spdeff + self.spe)