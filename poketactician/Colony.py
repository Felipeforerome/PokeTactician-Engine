import random
from collections import Counter
from math import ceil

import numpy as np
from numpy import array


class Colony:
    def __init__(
        self,
        pop_sizeParam,
        objFuncParam,
        poks,
        preSelected,
        preSelectedMoves,
        alpha,
        beta,
        Q,
        rho,
    ):
        self.pop_size = pop_sizeParam
        # objFunParam should be a lambda function
        self.objFunc = objFuncParam

        # Set Pokemon
        self.poks = poks

        # Set PreSelected Pokemon and Moves
        self.preSelectedPok = preSelected
        self.preSelectedMoves = preSelectedMoves

        # Set Meta Params
        self.alpha = alpha
        self.beta = beta
        self.Q = Q
        self.rho = rho

        # Create Decision Space of Pokemon
        self.DS_Pok = np.arange(self.poks.__len__())

        # Create Decision Space of Attacks
        self.DS_Att = [np.arange(len(pok.knowableMoves)) for pok in self.poks]

        # Create Probability Vector for Pokemon
        self.Prob_Poks = np.ones(self.poks.__len__()) * (1 / self.poks.__len__())

        # Create Probability of Attacks
        self.Prob_Att = []
        for pok in self.poks:
            size = pok.knowableMoves.__len__()
            if size == 0:
                self.Prob_Att.append([])
            else:
                self.Prob_Att.append(np.ones(size) * (1 / size))

        # Create Pheromone Vector for Pokemon
        self.Ph_Pok = np.zeros(self.poks.__len__())

        # Create Pheromone of Attacks
        self.Ph_Atts = []
        for pok in self.poks:
            size = pok.knowableMoves.__len__()
            if size == 0:
                size = 1
            self.Ph_Atts.append(np.zeros(size))

        # Create Heuristic Value of Pokemon
        self.H_Poks = np.zeros(self.poks.__len__())
        i = 0
        for i in range(0, self.H_Poks.__len__()):
            self.H_Poks[i] = self.heuristicPokFun(self.poks, i)

        # Create Heuristic Value of Attack
        self.H_Atts = []
        for pok in self.poks:
            size = pok.knowableMoves.__len__()
            if size == 0:
                size = 1
            self.H_Atts.append(np.zeros(size))

        # Create Population$
        # TODO Change to min(6, len(self.poks)) to 6 in case incomplete teams are not allowed
        self.Pop = np.ones([self.pop_size, min(6, len(self.poks)), 5], dtype=int) * (-1)

        # Initial Run of the Meta-Heuristic
        self.ACO()

    def ACO(self):
        # Assign Population
        for ant in self.Pop:
            # TODO Run more tests vectorized and non-vectorized versions they tend to give different results
            # TODO Allow Repeating even if not all pokemon have been used

            ######### Vectorized
            team_size = min(len(self.poks), 6)
            preSelected_size = len(self.preSelectedPok)
            ant[0:preSelected_size, 0] = self.preSelectedPok

            # Renormalize Probabilities
            self.Prob_Poks[self.preSelectedPok] = 0
            self.Prob_Poks /= self.Prob_Poks.sum()
            ant[preSelected_size:, 0] = np.random.choice(
                len(self.Prob_Poks),
                size=team_size - preSelected_size,
                replace=False,
                p=self.Prob_Poks,
            )
            ant[preSelected_size:, 0]
            # if replacePok:
            #     ant[len(self.poks) :, 0] = np.random.choice(
            #         len(self.Prob_Poks),
            #         size=6 - team_size,
            #         p=self.Prob_Poks,
            #     )
            for ant_i in range(ant.shape[0]):
                pokemon = ant[ant_i]
                selected_pokemon_id = pokemon[0]
                ######### NonVectorized
                prob_att_temp = self.Prob_Att[selected_pokemon_id].copy()
                for i in range(1, 5):
                    if ant_i < len(self.preSelectedMoves) and i - 1 < len(
                        self.preSelectedMoves[ant_i]
                    ):
                        pokemon[i] = self.preSelectedMoves[ant_i][i - 1]
                        prob_att_temp[self.preSelectedMoves[ant_i][i - 1]] = 0
                    elif prob_att_temp.size - i > 0:
                        rand_att = random.random() * prob_att_temp.sum()
                        cumulative_att_prob = np.cumsum(prob_att_temp)
                        selected_attack_id = np.argmax(rand_att <= cumulative_att_prob)

                        pokemon[i] = selected_attack_id
                        prob_att_temp[selected_attack_id] = 0
                    else:
                        pokemon[i] = -1
                ######### Vectorized
                # Get Knowable Moves
                # prob_att_temp = self.Prob_Att[selected_pokemon_id]
                # # TODO Ensure no repeated attacks and if the pokemon has less than 4 attacks, fill with -1 the remaining
                # num_req_atts = min(4, len(prob_att_temp))
                # selected_attack_ids = -1 * np.ones(4)
                # selected_attack_ids[0:num_req_atts] = np.random.choice(
                #     len(prob_att_temp),
                #     size=num_req_atts,
                #     replace=False,
                #     p=prob_att_temp,
                # )
                # pokemon[1:5] = selected_attack_ids

    def updatePhCon(self, candidateSet):
        # User Defined Variables
        Q = self.Q
        rho = self.rho
        # Update Pheromone Concentration
        # Evaporate Pheromones
        self.Ph_Pok = (1 - rho) * self.Ph_Pok
        for idx, Ph_Att in enumerate(self.Ph_Atts):
            self.Ph_Atts[idx] = (1 - rho) * Ph_Att

        for ant in candidateSet:
            fitnessValue = self.fitness(ant)
            deltaConcentr = Q * fitnessValue
            for pokemon in ant:
                self.Ph_Pok[pokemon[0]] = self.Ph_Pok[pokemon[0]] + deltaConcentr
                if pokemon[1] >= 0:
                    self.Ph_Atts[pokemon[0]][pokemon[1]] = (
                        self.Ph_Atts[pokemon[0]][pokemon[1]] + deltaConcentr
                    )

                if pokemon[2] >= 0:
                    self.Ph_Atts[pokemon[0]][pokemon[2]] = (
                        self.Ph_Atts[pokemon[0]][pokemon[2]] + deltaConcentr
                    )

                if pokemon[3] >= 0:
                    self.Ph_Atts[pokemon[0]][pokemon[3]] = (
                        self.Ph_Atts[pokemon[0]][pokemon[3]] + deltaConcentr
                    )

                if pokemon[4] >= 0:
                    self.Ph_Atts[pokemon[0]][pokemon[4]] = (
                        self.Ph_Atts[pokemon[0]][pokemon[4]] + deltaConcentr
                    )

    def updatePokProb(self):
        # Update Pokemon Probabilities
        numeratorsPok = self.numeratorFun(self.Ph_Pok, self.H_Poks)
        denomPok = self.numeratorFun(self.Ph_Pok, self.H_Poks).sum()
        if denomPok == 0:
            denomPok = 1
        for i in range(0, self.Prob_Poks.__len__()):
            self.Prob_Poks[i] = numeratorsPok[i] / denomPok

        # Update Attack Probabilities
        numeratorsAtt = []
        denomAtt = []
        for Ph_Att, H_Att in zip(self.Ph_Atts, self.H_Atts):
            temp = self.numeratorFun(Ph_Att, H_Att)
            numeratorsAtt.append(temp)
            denomAttTemp = temp.sum()
            if denomAttTemp == 0:
                denomAttTemp = 1
            denomAtt.append(denomAttTemp)

        for i in range(0, numeratorsAtt.__len__()):
            for j in range(0, numeratorsAtt[i].__len__()):
                if denomAtt[i] > 0:
                    self.Prob_Att[i][j] = numeratorsAtt[i][j] / denomAtt[i]

    def fitness(self, ant):
        fitnessValue = self.objFunc(ant)
        return fitnessValue

    def heuristicPokFun(self, poks, pokIndex):
        heuristicValue = poks[pokIndex].overallStats() / 500
        return heuristicValue

    def candidateSet(self):
        popSorted = sorted(self.Pop, key=self.fitness)
        return list(popSorted[ceil(self.pop_size * 0.90) : self.pop_size])

    def numeratorFun(self, c, n):
        return (c**self.alpha) * (n**self.beta)
