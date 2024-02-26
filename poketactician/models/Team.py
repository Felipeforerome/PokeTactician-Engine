class Team:
    def __init__(self):
        self.pokemons = []

    def addPokemon(self, pokemon):
        self.pokemons += [pokemon]

    def serialize(self):
        return [pokemon.serialize() for pokemon in self.pokemons]
