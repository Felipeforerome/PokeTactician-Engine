import numpy as np
import pickle
import random
import time
import glob_var
from math import ceil
from copy import deepcopy
from utils import currentPower, getLearnedMoves
###Ant Colony Optimization Algorithm

#General functions
numeratorFun = lambda c, n: (c ** alpha) + (n ** beta)

class Colony:

    def __init__(self, pop_sizeParam, objFuncParam, poks):
        self.pop_size = pop_sizeParam
        #objFunParam should be a lambda function
        self.objFunc = objFuncParam

        #Filter Pokemon (now not filtering)
        self.poks = poks


        #Create Decision Space of Pokemon
        self.DS_Pok = np.arange(self.poks.__len__())

        #Create Decision Space of Attacks
        self.DS_Att = []
        for pok in self.poks:
            size = pok.knowableMoves.__len__()
            self.DS_Att.append(np.arange(size))

        #Create Probability Vector for Pokemon
        self.Prob_Poks = np.ones(self.poks.__len__())*(1/self.poks.__len__())

        #Create Probability of Attacks
        self.Prob_Att = []
        for pok in self.poks:
            size = pok.knowableMoves.__len__()
            if(size == 0):
                size = 1
            self.Prob_Att.append(np.ones(size)*(1/size))

        #Create Pheromone Vector for Pokemon
        self.Ph_Pok = np.zeros(self.poks.__len__())


        #Create Pheromone of Attacks
        self.Ph_Atts = []
        for pok in self.poks:
            size = pok.knowableMoves.__len__()
            if(size == 0):
                size = 1
            self.Ph_Atts.append(np.zeros(size))

        #Create Heuristic Value of Pokemon
        self.H_Poks = np.zeros(self.poks.__len__())
        i = 0
        for i in range(0, self.H_Poks.__len__()):
            self.H_Poks[i] = self.heuristicPokFun(self.poks, i)

        #Create Heuristic Value of Attack
        self.H_Atts = []
        for pok in self.poks:
            size = pok.knowableMoves.__len__()
            if(size == 0):
                size = 1
            self.H_Atts.append(np.zeros(size))

        #Create Population
        self.Pop = np.empty([self.pop_size,6,5], dtype=int)

        #Initial Run of the Meta-Heuristic
        self.ACO()



    def ACO(self):
        #Assign Population
        for ant in self.Pop:
            for pokemon in ant:
                selectedPok = False
                id = 0
                tempSum = 0
                randPok = random.randrange(0,100001,1)/100001
                #Get Pokemon such that ph_(n)< rand <ph(n+1)
                while(not selectedPok):
                    tempProb = self.Prob_Poks[id]
                    if(randPok>tempSum+tempProb):
                        id = id + 1
                        tempSum = tempSum + tempProb
                    elif(randPok<tempSum+tempProb):
                        selectedPok = True

                pokemon[0] = id

                #Get Knowable Moves
                ProbAtt_Temp = deepcopy(self.Prob_Att[id])
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

    def updatePhCon(self, candidateSet):
        # User Defined Variables
        Q = glob_var.Q
        rho = glob_var.rho

        #Update Pheromone Concentration
        #Evaporate Pheromones
        self.Ph_Pok = (1-rho)*self.Ph_Pok

        for idx, Ph_Att in enumerate(self.Ph_Atts):
            self.Ph_Atts[idx] = (1-rho)*Ph_Att

        for ant in candidateSet:
            fitnessValue = self.fitness(ant)
            deltaConcentr = Q*fitnessValue
            for pokemon in ant:
                self.Ph_Pok[pokemon[0]] = self.Ph_Pok[pokemon[0]]+deltaConcentr
                if pokemon[1]>=0:
                    self.Ph_Atts[pokemon[0]][pokemon[1]] = self.Ph_Atts[pokemon[0]][pokemon[1]]+deltaConcentr

                if pokemon[2]>=0:
                    self.Ph_Atts[pokemon[0]][pokemon[2]] = self.Ph_Atts[pokemon[0]][pokemon[2]]+deltaConcentr

                if pokemon[3]>=0:
                    self.Ph_Atts[pokemon[0]][pokemon[3]] = self.Ph_Atts[pokemon[0]][pokemon[3]]+deltaConcentr

                if pokemon[4]>=0:
                    self.Ph_Atts[pokemon[0]][pokemon[4]] = self.Ph_Atts[pokemon[0]][pokemon[4]]+deltaConcentr

    def updatePokProb(self):
        #Update Pokemon Probabilities
        numeratorsPok = numeratorFun(self.Ph_Pok, self.H_Poks)
        denomPok = numeratorFun(self.Ph_Pok,self.H_Poks).sum()
        for i in range(0,self.Prob_Poks.__len__()):
            self.Prob_Poks[i] = numeratorsPok[i]/denomPok

        #Update Attack Probabilities
        numeratorsAtt=[]
        denomAtt=[]
        for Ph_Att, H_Att in zip(self.Ph_Atts, self.H_Atts):
            temp = numeratorFun(Ph_Att, H_Att)
            numeratorsAtt.append(temp)
            denomAtt.append(temp.sum())

        for i in range(0, numeratorsAtt.__len__()):
            for j in range(0, numeratorsAtt[i].__len__()):
                self.Prob_Att[i][j] = numeratorsAtt[i][j]/denomAtt[i]

    def fitness(self, ant):
        fitnessValue = self.objFunc(ant)
        return fitnessValue

    def heuristicPokFun(self, poks, pokIndex):
        heuristicValue = poks[pokIndex].overallStats()/500
        return heuristicValue

if __name__ == "__main__":
    #import pokemon DB
    with open("Pok.pkl", "rb") as f:
        pokPreFilter = pickle.load(f)
    with open("Moves.pkl", "rb") as f:
        moves = pickle.load(f)
    objFunctionOne = lambda team: sum(list(map(lambda x: currentPower(pokPreFilter[x[0]],getLearnedMoves(pokPreFilter, x, x[1],x[2],x[3],x[4])), team)))
    tic = time.time()
    firstColony = Colony(5000,objFunctionOne, pokPreFilter)
    toc = time.time()
    print(toc-tic)
    print(firstColony.Pop)