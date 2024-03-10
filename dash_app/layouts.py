from dash import html, dcc
import dash_mantine_components as dmc

from dash_iconify import DashIconify

# Define the layout
layout = html.Div(
    children=[
        # Variable share
        dcc.Store(id="memory-output"),
        dmc.Modal(
            title=dmc.Group(
                [
                    DashIconify(icon="arcticons:pokemon-unite"),
                    dmc.Text("🌟 Hello and Welcome to PokéTactician! 🌟", weight=700),
                    DashIconify(icon="arcticons:pokemon-unite"),
                ]
            ),
            id="modal-centered",
            centered=True,
            size="55%",
            zIndex=10000,
            children=[
                dmc.Text(
                    "This is a project I've developed in my free time to put some theory to practice and have fun with my passion for Pokemon. This webapp started as a way for me to practice implementing some Multi Objective Metaheuristic Algorithms to solve NP-Hard problems, and practice frontend development. It has been developed with the goal of providing a tool for different people to use and tailor the results they want to get. It is built implementing a Multi Objective Ant Colony Optimization for the composition of the team, and Dash with Dash Mantine for the interface."
                ),
            ],
            opened=True,
        ),
        # Header
        html.Header(
            children=[
                html.Div(
                    children=[
                        # Title or logo on the left
                        html.H1(
                            "PokéTactician",
                            style={
                                "flex": 1,
                                "color": "#F7CE46",
                                "textAlign": "left",
                                "textShadow": "-1px 1px 0 #000,1px 1px 0 #000,1px -1px 0 #000,-1px -1px 0 #000;",
                            },
                        ),
                        # Navigation links on the right
                        html.Div(
                            children=[
                                html.A(
                                    "Home",
                                    href="/",
                                    style={"marginRight": "15px", "color": "white"},
                                ),
                                html.A(
                                    "Contact",
                                    href="mailto:felipe.forerome@gmail.com",
                                    style={"color": "white"},
                                ),
                            ],
                            style={"flex": 1, "textAlign": "right"},
                        ),
                    ],
                    style={
                        "display": "flex",
                        "alignItems": "center",
                        "justifyContent": "space-between",
                    },
                )
            ],
            style={
                "backgroundColor": "#3E65AB",
                "padding": "10px",
                "marginBottom": "25px",
            },
        ),
        # Main content flex container
        html.Div(
            style={"display": "flex", "height": "calc(100vh - 56px)"},
            children=[
                # NavBar for filters
                dmc.Navbar(
                    p="md",
                    width={"base": 300},
                    fixed=False,
                    children=[
                        dmc.MultiSelect(
                            label="Select Objectives",
                            placeholder="",
                            id="objectives-multi-select",
                            value=[1],
                            data=[
                                {"value": 1, "label": "Attack"},
                                {"value": 2, "label": "Team Coverage"},
                                {"value": 3, "label": "Self Coverage"},
                            ],
                            style={"marginBottom": 10, "width": "95%"},
                            required=True,
                            withAsterisk=False,
                        ),
                        html.Br(),
                        dmc.MultiSelect(
                            label="Select Types to Include",
                            placeholder="Leave empty for all",
                            id="type-multi-select",
                            value=[],
                            data=[
                                {"value": "normal", "label": "Normal"},
                                {"value": "fire", "label": "Fire"},
                                {"value": "water", "label": "Water"},
                                {"value": "electric", "label": "Electric"},
                                {"value": "grass", "label": "Grass"},
                                {"value": "ice", "label": "Ice"},
                                {"value": "fighting", "label": "Fighting"},
                                {"value": "poison", "label": "Poison"},
                                {"value": "ground", "label": "Ground"},
                                {"value": "flying", "label": "Flying"},
                                {"value": "psychic", "label": "Psychic"},
                                {"value": "bug", "label": "Bug"},
                                {"value": "rock", "label": "Rock"},
                                {"value": "ghost", "label": "Ghost"},
                                {"value": "dragon", "label": "Dragon"},
                                {"value": "dark", "label": "Dark"},
                                {"value": "steel", "label": "Steel"},
                                {"value": "fairy", "label": "Fairy"},
                            ],
                            style={"marginBottom": 10, "width": "95%"},
                        ),
                        html.Br(),
                        dmc.Switch(
                            label="Only Mono-types?",
                            offLabel="No",
                            onLabel="Yes",
                            checked=False,
                            id="mono-type",
                        ),
                        html.Br(),
                        dmc.Button(
                            "Suggest Team",
                            leftIcon=DashIconify(icon="ic:twotone-catching-pokemon"),
                            color="indigo",
                            id="suggest-team-btn",
                        ),
                    ],
                ),
                # Container for results
                dmc.Container(
                    style={
                        "flexGrow": 1,
                        "marginLeft": 20,
                        "marginRight": 20,
                        "overflow": "auto",
                        "maxWidth": "none",  # Removes the max-width restriction
                        "width": "100%",  # Optionally, ensure it takes the full width available
                    },
                    children=[
                        dcc.Loading(
                            id="loading-output",
                            children=[
                                html.Br(),
                                html.Div(id="time-to-calc"),
                                html.Br(),
                                html.Div(id="team-output"),
                                html.Br(),
                                html.Div(style={"display": "none"}, id="placeholder"),
                            ],
                            type="default",
                        ),
                    ],
                ),
            ],
        ),
        dmc.Footer(
            height=60,
            fixed=False,
            children=[
                dmc.Center(
                    children=[
                        dmc.Text("Made by Felipe Forero Meola"),
                    ]
                ),
                dmc.Center(
                    children=[
                        html.Br(),
                        dmc.Text("Pokémon is © of Nintendo"),
                    ]
                ),
            ],
            style={"color": "grey"},
        ),
    ]
)
