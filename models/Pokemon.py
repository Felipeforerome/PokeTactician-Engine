class Pokemon:
    def __init__(self, name, hp, att, deff, spatt, spdeff, spe, type1, type2):
        self.name = name
        self.hp = hp
        self.att = att
        self.deff = deff
        self.spatt = spatt
        self.spdeff = spdeff
        self.spe = spe
        self.learnedMoves = []
        self.moves = []
        self.type1 = type1
        self.type2 = type2
        self.knowableMoves = []

    def addKnowableMove(self, move):
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


    def addMove(self, move):
        self.moves.append(move)

    def expectedMoves(self):
        moves = self.moves
        expectedAttacks = []
        for move in moves:
            moveName = move.Name
            moveType = move.type
            movePower = move.power
            moveDamageClass = move.damageClass
            moveAccuracy = move.accuracy
            stab = 1.5 if (moveType == self.type1 or moveType == self.type2) else 1
            split = self.att if (moveDamageClass == "physical") else self.spatt
            expectedPower = (stab * movePower) * split * moveAccuracy
            expectedAttacks.append((moveName, expectedPower))
        return expectedAttacks

    def learnMove(self, move, place=None):
        if(place==None):
            numberMoves = self.learnedMoves.__len__()
            if(numberMoves<4):
                self.learnedMoves[place] = move
            else:
                raise Exception("Missing Place Argument, This Pokemon Already Knows 4 Moves")

    def currentPower(self):
        currentPower = 0
        if self.learnedMoves.__len__() <1:
            raise Exception("This Pokemon Needs To Learn A Move")
        else:
            for learnedMove in self.learnedMoves:
                moveType = learnedMove.type
                movePower = learnedMove.power
                moveDamageClass = learnedMove.damageClass
                moveAccuracy = learnedMove.accuracy
                stab = 1.5 if (moveType == self.type1 or moveType == self.type2) else 1
                split = self.att if (moveDamageClass == "physical") else self.spatt
                expectedPower = (stab * movePower) * split * moveAccuracy
                currentPower += expectedPower
            return currentPower

    def overallStats(self):
        return (self.hp + self.att + self.deff + self.spatt + self.spdeff + self.spe)