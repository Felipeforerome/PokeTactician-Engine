import numpy as np
import pickle
import random
import time
#Ant Colony Optimization Algorithm

def ACO(filter=None):
    tic = time.time()
    #import pokemon DB
    with open("Pok.pkl", "rb") as f:
        pokPreFilter = pickle.load(f)

    #Filter Pokemon (now not filtering)
    poks = pokPreFilter


    #Create Decision Space of Pokemon
    DS_Pok = np.arange(poks.__len__())

    #Create Pheromone Vector for Pokemon
    Ph_Pok = np.ones(poks.__len__())*(1/poks.__len__())

    #Create Decision Space of Attacks
    DS_Att = []
    for pok in poks:
        size = pok.knowableMoves.__len__()
        DS_Att.append(np.arange(size))

    #Create Pheromone of Attacks
    Ph_Att = []
    for pok in poks:
        size = pok.knowableMoves.__len__()
        if(size == 0):
            size = 1
        Ph_Att.append(np.ones(size)*(1/size))

    #Create Population
    pop_size = 100
    Pop = np.empty([pop_size,6,5])

    #Assign Population
    for ant in Pop:
        for pokemon in ant:
            selectedPok = False
            id = 0
            tempSum = 0
            randPok = random.randrange(0,100001,1)/100001
            #Get Pokemon such that ph_(n)< rand <ph(n+1)
            while(not selectedPok):
                tempPh = Ph_Pok[id]
                if(randPok>tempSum+tempPh):
                    id = id + 1
                    tempSum = tempSum + tempPh
                elif(randPok<tempSum+tempPh):
                    selectedPok = True

            pokemon[0] = id

            #Get Knowable Moves
            PhAtt_Temp = Ph_Att[id]
            for i in range(1,5):
                if((PhAtt_Temp.size - (i))>0):
                    randAtt = PhAtt_Temp.sum()*random.randrange(0,100001,1)/100001
                    attId = 0
                    tempSum = 0
                    selectedAttack = False
                    while(not selectedAttack):
                        tempPh = PhAtt_Temp[attId]
                        if(randAtt>tempSum+tempPh):
                            attId = attId + 1
                            tempSum = tempSum + tempPh
                        elif(randAtt<=tempSum+tempPh):
                            pokemon[i] = poks[id].knowableMoves[attId].id
                            PhAtt_Temp[attId] = 0
                            selectedAttack = True
                else:
                    pokemon[i] = -1

    toc = time.time()
    print(toc-tic)
    print("Stop")







def fitness():
    fitnessValue = 0

    return fitnessValue

def calculatePheromone(ph_vect):
    pass


if __name__ == "__main__":
    ACO()