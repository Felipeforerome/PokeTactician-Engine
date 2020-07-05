import numpy as np
import pickle
import random
import time
from copy import deepcopy
###Ant Colony Optimization Algorithm

#User Defined Variables
Q = 10
rho = 0.2
alpha = 1
beta = 1

#General functions
numeratorFun = lambda c, n: (c ** alpha) + (n ** beta)

def ACO(filter=None):
    tic = time.time()
    #import pokemon DB
    with open("Pok.pkl", "rb") as f:
        pokPreFilter = pickle.load(f)

    #Filter Pokemon (now not filtering)
    poks = pokPreFilter


    #Create Decision Space of Pokemon
    DS_Pok = np.arange(poks.__len__())

    #Create Decision Space of Attacks
    DS_Att = []
    for pok in poks:
        size = pok.knowableMoves.__len__()
        DS_Att.append(np.arange(size))

    #Create Probability Vector for Pokemon
    Prob_Poks = np.ones(poks.__len__())*(1/poks.__len__())

    #Create Probability of Attacks
    Prob_Att = []
    for pok in poks:
        size = pok.knowableMoves.__len__()
        if(size == 0):
            size = 1
        Prob_Att.append(np.ones(size)*(1/size))

    #Create Pheromone Vector for Pokemon
    Ph_Pok = np.zeros(poks.__len__())


    #Create Pheromone of Attacks
    Ph_Att = []
    for pok in poks:
        size = pok.knowableMoves.__len__()
        if(size == 0):
            size = 1
        Ph_Att.append(np.zeros(size))

    #Create Heuristic Value of Pokemon
    H_Poks = np.zeros(poks.__len__())
    i = 0
    for i in range(0, H_Poks.__len__()):
        H_Poks[i] = heuristicPokFun(poks, i)

    #Create Heuristic Value of Attack
    H_Att = []
    for pok in poks:
        size = pok.knowableMoves.__len__()
        if(size == 0):
            size = 1
        H_Att.append(np.zeros(size))

    #Create Population
    pop_size = 5000
    Pop = np.empty([pop_size,6,5], dtype=int)

    #Assign Population
    for ant in Pop:
        for pokemon in ant:
            selectedPok = False
            id = 0
            tempSum = 0
            randPok = random.randrange(0,100001,1)/100001
            #Get Pokemon such that ph_(n)< rand <ph(n+1)
            while(not selectedPok):
                tempProb = Prob_Poks[id]
                if(randPok>tempSum+tempProb):
                    id = id + 1
                    tempSum = tempSum + tempProb
                elif(randPok<tempSum+tempProb):
                    selectedPok = True

            pokemon[0] = id

            #Get Knowable Moves
            ProbAtt_Temp = deepcopy(Prob_Att[id])
            for i in range(1,5):
                if((ProbAtt_Temp.size - (i))>0):
                    randAtt = ProbAtt_Temp.sum()*random.randrange(0,100001,1)/100001
                    attId = 0
                    tempSum = 0
                    selectedAttack = False
                    while(not selectedAttack):
                        tempPh = ProbAtt_Temp[attId]
                        if(randAtt>tempSum+tempPh):
                            attId = attId + 1
                            tempSum = tempSum + tempPh
                        elif(randAtt<=tempSum+tempPh):
                            pokemon[i] = attId
                            ProbAtt_Temp[attId] = 0
                            selectedAttack = True
                else:
                    pokemon[i] = -1

    #Update Pheromone Concentration
    for ant in Pop:
        fitnessValue = fitness(ant)
        deltaConcentr = Q*fitnessValue
        for pokemon in ant:
            Ph_Pok[pokemon[0]] = (1-rho)*Ph_Pok[pokemon[0]]+deltaConcentr
            if pokemon[1]>=0:
                Ph_Att[pokemon[0]][pokemon[1]] = (1-rho)*Ph_Att[pokemon[0]][pokemon[1]]+deltaConcentr

            if pokemon[2]>=0:
                Ph_Att[pokemon[0]][pokemon[2]] = (1-rho)*Ph_Att[pokemon[0]][pokemon[2]]+deltaConcentr

            if pokemon[3]>=0:
                Ph_Att[pokemon[0]][pokemon[3]] = (1-rho)*Ph_Att[pokemon[0]][pokemon[3]]+deltaConcentr

            if pokemon[4]>=0:
                Ph_Att[pokemon[0]][pokemon[4]] = (1-rho)*Ph_Att[pokemon[0]][pokemon[4]]+deltaConcentr

    #Update Pokemon Probabilities
    numeratorsPok = numeratorFun(Ph_Pok, H_Poks)
    denomPok = numeratorFun(Ph_Pok,H_Poks).sum()
    for i in range(0,Prob_Poks.__len__()):
        Prob_Poks[i] = numeratorsPok[i]/denomPok

    #Update Attack Probabilities
    numeratorsAtt=[]
    denomAtt=[]
    for PhAtt, HAtt in zip(Ph_Att, H_Att):
        temp = numeratorFun(PhAtt, HAtt)
        numeratorsAtt.append(temp)
        denomAtt.append(temp.sum())

    for i in range(0, numeratorsAtt.__len__()):
        for j in range(0, numeratorsAtt[i].__len__()):
            Prob_Att[i][j] = numeratorsAtt[i][j]/denomAtt[i]

    toc = time.time()
    print(toc-tic)
    print("Stop")


def fitness(ant):
    fitnessValue = 1

    return fitnessValue

def calculatePheromone(ph_vect):
    pass

def heuristicPokFun(poks, pokIndex):
    #TODO Scale the heuristic value after getting Pheromone Values
    heuristicValue = poks[pokIndex].overallStats()/500
    return heuristicValue

if __name__ == "__main__":
    ACO()