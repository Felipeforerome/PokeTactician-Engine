import random
from math import ceil

import numpy as np

from .models.Team import Team


class Colony:
    def __init__(
        self,
        pop_size_param,
        objective_fun_param,
        pokemons_param,
        preselected_poks,
        preselected_moves,
        alpha,
        beta,
        Q,
        rho,
        roles=[],
    ):
        self.pop_size = pop_size_param
        # objFunParam should be a lambda function
        self.objective_function = objective_fun_param

        # Set Pokemon
        self.pokemons = pokemons_param

        # Set PreSelected Pokemon and Moves
        self.preselected_pok = preselected_poks
        self.preselected_moves = preselected_moves

        # Set Roles
        self.roles = roles

        # Set Meta Params
        self.alpha = alpha
        self.beta = beta
        self.Q = Q
        self.rho = rho

        # Create Decision Space of Pokemon
        self.decision_space_pokemon = np.arange(self.pokemons.__len__())

        # Create Decision Space of Moves
        self.decision_space_moves = [
            np.arange(len(pok.knowable_moves)) for pok in self.pokemons
        ]

        # Create Probability Vector for Pokemon
        self.pokemon_probabilities = np.ones(self.pokemons.__len__()) * (
            1 / self.pokemons.__len__()
        )

        # Create Probability of Attacks
        self.move_probabilities = []
        for pokemon in self.pokemons:
            size = pokemon.knowable_moves.__len__()
            if size == 0:
                self.move_probabilities.append([])
            else:
                self.move_probabilities.append(np.ones(size) * (1 / size))

        # Create Pheromone Vector for Pokemon
        self.pokemon_pheromones = np.zeros(self.pokemons.__len__())

        # Create Pheromone of Attacks
        self.move_pheromones = []
        for pokemon in self.pokemons:
            size = pokemon.knowable_moves.__len__()
            if size == 0:
                size = 1
            self.move_pheromones.append(np.zeros(size))

        # Create Heuristic Value of Pokemon
        self.pokemon_heuritics = np.zeros(self.pokemons.__len__())
        i = 0
        for i in range(0, self.pokemon_heuritics.__len__()):
            self.pokemon_heuritics[i] = self.heuristic_pokemon_fun(self.pokemons, i)

        # Create Heuristic Value of Attack
        self.move_heuristics = []
        for pokemon in self.pokemons:
            size = pokemon.knowable_moves.__len__()
            if size == 0:
                size = 1
            self.move_heuristics.append(np.zeros(size))

        # Create Population$
        # TODO Change min(6, len(self.poks)) to 6 in case incomplete teams are not allowed
        self.population = np.ones(
            [self.pop_size, min(6, len(self.pokemons)), 5], dtype=int
        ) * (-1)

        # Initial Run of the Meta-Heuristic
        self.ACO()

    def role_constraint(self, ant):
        team = Team.ant_to_team(ant, self.pokemons)
        team.team_has_roles(self.roles)
        return True

    def create_ant(self):
        # TODO Run more tests vectorized and non-vectorized versions they tend to give different results
        # TODO Allow Repeating even if not all pokemon have been used

        ######### Vectorized
        ant = np.ones([min(6, len(self.pokemons)), 5], dtype=int) * (-1)
        team_size = min(len(self.pokemons), 6)
        preselected_size = len(self.preselected_pok)
        ant[0:preselected_size, 0] = self.preselected_pok
        if preselected_size < team_size:

            # Renormalize Probabilities
            self.pokemon_probabilities[self.preselected_pok] = 0
            self.pokemon_probabilities /= self.pokemon_probabilities.sum()
            ant[preselected_size:, 0] = np.random.choice(
                len(self.pokemon_probabilities),
                size=team_size - preselected_size,
                replace=False,
                p=self.pokemon_probabilities,
            )
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
            prob_att_temp = self.move_probabilities[selected_pokemon_id].copy()
            for i in range(1, 5):
                if ant_i < len(self.preselected_moves) and i - 1 < len(
                    self.preselected_moves[ant_i]
                ):
                    pokemon[i] = self.preselected_moves[ant_i][i - 1]
                    prob_att_temp[self.preselected_moves[ant_i][i - 1]] = 0
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
        return ant

    def ACO(self):
        # Assign Population
        for i in range(self.pop_size):
            temp_ant = self.create_ant()
            while len(self.roles) > 0 and not self.role_constraint(temp_ant):
                temp_ant = self.create_ant()
            self.population[i] = temp_ant

    def update_ph_concentration(self, candidate_set):
        # User Defined Variables
        Q = self.Q
        rho = self.rho
        # Update Pheromone Concentration
        # Evaporate Pheromones
        self.pokemon_pheromones = (1 - rho) * self.pokemon_pheromones
        for idx, move_pheromone in enumerate(self.move_pheromones):
            self.move_pheromones[idx] = (1 - rho) * move_pheromone

        for ant in candidate_set:
            fitness_value = self.fitness(ant)
            delta_concentration = Q * fitness_value
            for pokemon in ant:
                self.pokemon_pheromones[pokemon[0]] = (
                    self.pokemon_pheromones[pokemon[0]] + delta_concentration
                )
                if pokemon[1] >= 0:
                    self.move_pheromones[pokemon[0]][pokemon[1]] = (
                        self.move_pheromones[pokemon[0]][pokemon[1]]
                        + delta_concentration
                    )

                if pokemon[2] >= 0:
                    self.move_pheromones[pokemon[0]][pokemon[2]] = (
                        self.move_pheromones[pokemon[0]][pokemon[2]]
                        + delta_concentration
                    )

                if pokemon[3] >= 0:
                    self.move_pheromones[pokemon[0]][pokemon[3]] = (
                        self.move_pheromones[pokemon[0]][pokemon[3]]
                        + delta_concentration
                    )

                if pokemon[4] >= 0:
                    self.move_pheromones[pokemon[0]][pokemon[4]] = (
                        self.move_pheromones[pokemon[0]][pokemon[4]]
                        + delta_concentration
                    )

    def update_pokemon_prob(self):
        # Update Pokemon Probabilities
        pokemon_numerators = self.numerator_fun(
            self.pokemon_pheromones, self.pokemon_heuritics
        )
        pokemon_denominators = self.numerator_fun(
            self.pokemon_pheromones, self.pokemon_heuritics
        ).sum()
        if pokemon_denominators == 0:
            pokemon_denominators = 1
        for i in range(0, self.pokemon_probabilities.__len__()):
            self.pokemon_probabilities[i] = pokemon_numerators[i] / pokemon_denominators

        # Update Attack Probabilities
        move_numerators = []
        move_denominators = []
        for move_pheromone, move_heuristic in zip(
            self.move_pheromones, self.move_heuristics
        ):
            temp = self.numerator_fun(move_pheromone, move_heuristic)
            move_numerators.append(temp)
            temp_move_denominator = temp.sum()
            if temp_move_denominator == 0:
                temp_move_denominator = 1
            move_denominators.append(temp_move_denominator)

        for i in range(0, move_numerators.__len__()):
            for j in range(0, move_numerators[i].__len__()):
                if move_denominators[i] > 0:
                    self.move_probabilities[i][j] = (
                        move_numerators[i][j] / move_denominators[i]
                    )

    def fitness(self, ant):
        fitness_value = self.objective_function(ant)
        return fitness_value

    def heuristic_pokemon_fun(self, pokemon, pokemon_index):
        heuristic_value = pokemon[pokemon_index].overall_stats() / 500
        return heuristic_value

    def candidate_set(self):
        sorted_population = sorted(self.population, key=self.fitness)
        return list(sorted_population[ceil(self.pop_size * 0.90) : self.pop_size])

    def numerator_fun(self, c, n):
        return (c**self.alpha) * (n**self.beta)
