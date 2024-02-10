class Team:
    def __init__(self):
        self.pokemons = []

    def addPokemon(self, newPokemon):
        if(self.pokemons.__len__() < 6):
            self.pokemons.append(newPokemon)
        else:
            raise Exception("You already have 6 Pokemon in the Team")

    def removePokemon(self, removePokemon):
        self.pokemons.remove(removePokemon)

    def teamPower (self):
        teamPower = 0
        if (self.pokemons.__len__()==0):
            raise Exception("The Team is empty, you need to add a Pokemon")
        else:
            for pokemon in self.pokemons:
                teamPower += pokemon.currentPower()
        return teamPower