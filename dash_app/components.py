from dash import html, dcc
import dash_mantine_components as dmc

from dash_iconify import DashIconify


class PokemonCard:
    def __init__(
        self,
        pokemon: dict,
    ):
        self.pokemon = pokemon

    def layout(self):
        pokemon = self.pokemon
        return dmc.Card(
            children=[
                dmc.CardSection(
                    children=[
                        dmc.Image(
                            src="https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/17.png",
                            height="75%",
                            width="75%",
                            style={"margin": "auto"},
                        ),
                        dmc.Center(  # Use dmc.Center for center alignment
                            dmc.Text(
                                pokemon["name"].title(),
                                weight=500,
                            ),
                        ),
                    ],
                    withBorder=True,
                    inheritPadding=True,
                    py="xs",
                ),
                dmc.CardSection(
                    children=[
                        dmc.SimpleGrid(
                            cols=2,
                            children=[
                                html.P(
                                    move["name"].replace("-", " ").title(),
                                    className="card-content",
                                )
                                for move in pokemon["moves"]
                            ],
                        ),
                    ],
                    inheritPadding=True,
                    mt="sm",
                    pb="md",
                ),
            ],
            withBorder=True,
            shadow="sm",
            radius="md",
            style={"width": "20vw"},
        )


class PokemonTeam:
    def __init__(self, pokemonList):
        self.pokemonCards = [
            dmc.Col(
                PokemonCard(pokemon).layout(),
                span=4,
            )
            for pokemon in pokemonList
        ]

    def layout(self):
        return dmc.Grid(
            children=self.pokemonCards, className="team", justify="space-evenly"
        )
