from Colony import Colony
import itertools
import pickle
import time
import glob_var
import csv
from multiprocessing import Pool
from copy import deepcopy
from utils import currentPower, getLearnedMoves

def dataGathering():
    tic = time.time()
    data_header = [["Q", "Rho", "Run", "1" , "2" , "3" , "4" , "5" , "6" , "7" , "8" , "9" , "10" , "11" , "12" , "13" , "14" , "15" , "16" , "17" , "18" , "19" , "20" , "21" , "22" , "23" , "24" , "25" , "26" , "27" , "28" , "29" , "30" , "31" , "32" , "33" , "34" , "35" , "36" , "37" , "38" , "39" , "40" , "41" , "42" , "43" , "44" , "45" , "46" , "47" , "48" , "49" , "50"]]
    p = Pool(processes=8)
    data_mp = p.map(runAlgo, itertools.product(range(1,21), range(0,21)))
    p.close()
    toc = time.time()
    print(toc-tic)
    data = data_header
    for i in data_mp:
        data = data + i
    with open('data.csv', 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerows(data)

    with open("data.pkl", "wb") as f:
        pickle.dump(data, f)

def runAlgo(params):
    data = []
    qStep = params[0]
    rhoStep = params[1]
    glob_var.Q = (qStep / 20) * 1000
    glob_var.rho = rhoStep / 20
    print(params)
    Q = glob_var.Q
    rho = glob_var.rho

    with open("Pok.pkl", "rb") as f:
        pokPreFilter = pickle.load(f)
    with open("Moves.pkl", "rb") as f:
        moves = pickle.load(f)
    objFunctionOne = lambda team: sum(list(
        map(lambda x: currentPower(pokPreFilter[x[0]], getLearnedMoves(pokPreFilter, x, [x[1], x[2], x[3], x[4]])),
            team)))
    firstColony = Colony(500, objFunctionOne, pokPreFilter)
    prevCandSet = firstColony.candidateSet()
    for i in range(1, 26):
        a = list(map(objFunctionOne, prevCandSet))
        dataCandSet = [Q] + [rho] + [i] + a
        data += [dataCandSet]
        # b = np.array(a)
        # plt.scatter(range(0, b.size), b)
        # plt.title("Iter: "+ str(i) + " - rho: "+str(rho)+ " - Q: "+str(Q))
        # plt.show()
        currentCandSet = firstColony.candidateSet()
        updateSet = deepcopy(prevCandSet) + deepcopy(currentCandSet)
        candSetTemp = list(sorted(updateSet, key=firstColony.fitness))
        candSet = candSetTemp[int(candSetTemp.__len__() / 2):candSetTemp.__len__()]
        prevCandSet = candSet
        firstColony.updatePhCon(candSet)
        firstColony.updatePokProb()
        firstColony.ACO()
    return data

if __name__ == "__main__":
    dataGathering()