import numpy as np
import matplotlib.pyplot as plt
import pickle
import glob_var
from copy import deepcopy
from functools import reduce
from utils import currentPower, getLearnedMoves, getWeakness, colonyCooperation
from Colony import Colony

###Multi Objective Ant Colony Optimization Algorithm

# import pokemon DB
with open("Pok.pkl", "rb") as f:
    pokPreFilter = pickle.load(f)
with open("Moves.pkl", "rb") as f:
    moves = pickle.load(f)

def MOACO(totalPopulation, objFuncs):

    colonies = [Colony(int(totalPopulation/objFuncs.__len__()), objFunc, pokPreFilter) for objFunc in objFuncs]
    coopCandSet = colonyCooperation([colony.candidateSet() for colony in colonies], objFuncs)

    prevCandSet = coopCandSet
    iters = 26
    for i in range(0,iters):
        jointFun = lambda team: attackObjFun(team)*selfCoverageFun(team)
        a = sorted(list(map(jointFun, prevCandSet)))
        b = np.array(a)
        plt.scatter(range(0, b.size), b)
        plt.title("Iter: "+ str(i) + " - rho: "+str(glob_var.rho)+ " - Q: "+str(glob_var.Q))
        plt.show()
        for colony in colonies:
            colony.updatePhCon(prevCandSet)
            colony.updatePokProb()
            colony.ACO()
        currentCandSet = deepcopy(colonyCooperation([colony.candidateSet() for colony in colonies], objFuncs))
        prevCandSet = deepcopy(colonyCooperation([prevCandSet, currentCandSet], objFuncs))

    print(currentCandSet[0])


if __name__ == "__main__":
    attackObjFun = lambda team: sum(list(map(lambda x: currentPower(pokPreFilter[x[0]], getLearnedMoves(pokPreFilter, x, [x[1], x[2], x[3], x[4]])), team)))
    #TODO Fix magnitud function it's encouraging increasing single type coverage, should aim for spread
    #selfCoverageFun = lambda team: 1/reduce(np.multiply,map(hoyerSparseness,map(lambda x: getWeakness(pokPreFilter[x[0]]), team)))
    selfCoverageFun = lambda team: 1 / np.power(
        np.ones_like(reduce(np.multiply, map(lambda x: getWeakness(pokPreFilter[x[0]]), team))) * 2,
        reduce(np.multiply, map(lambda x: getWeakness(pokPreFilter[x[0]]), team))).mean()
    MOACO(1000, [attackObjFun, selfCoverageFun])