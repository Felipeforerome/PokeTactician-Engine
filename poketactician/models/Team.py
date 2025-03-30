from dataclasses import dataclass, field

from .Pokemon import Pokemon


@dataclass
class Team:
    pokemons: list[Pokemon] = field(default_factory=list)

    def add_pokemon(self, pokemon: Pokemon) -> None:
        if len(self.pokemons) < 6:
            self.pokemons += [pokemon]
        else:
            raise Exception("Team is full")

    @classmethod
    def ant_to_team(cls, ant, pokemons_list: list):
        team = cls()
        for pok in ant:
            temp_pok = Pokemon.from_json(pokemons_list[pok[0]].serialize())
            temp_pok.teach_move(pok[1])
            temp_pok.teach_move(pok[2])
            temp_pok.teach_move(pok[3])
            temp_pok.teach_move(pok[4])
            team.add_pokemon(temp_pok)
        return team

    def team_has_roles(self, roles: list[callable]) -> bool:
        for role in roles:
            role_fulfilled = False
            for pokemon in self.pokemons:
                if pokemon.is_role(role) > 0:
                    role_fulfilled = True
                    break
            if not role_fulfilled:
                return False
        return True

    def team_roles_fun(self, roles: list = []) -> float:
        """
        Calculates the total score of Pokémon in a team that have the specified roles.

        Args:
            roles (list, optional): A list of strings representing the roles to check. Defaults to [].

        Returns:
            float: The total number of Pokémon in the team that have the specified roles.
        """
        return sum([pok.is_role(role) for pok in self.pokemons for role in roles])

    def serialize(self) -> list:
        return [{"pokemon": pokemon.id, "moves": [move.id for move in pokemon.learnt_moves]} for pokemon in self.pokemons]
