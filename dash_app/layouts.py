import dash_mantine_components as dmc
from components import (
    BlankPokemonCard,
    BlankPokemonTeam,
    drawer_filter_components,
    navbar_filter_components,
)
from dash import dcc, html
from dash_iconify import DashIconify
from decouple import config

# Define the layout
layout = html.Div(
    children=[
        # Variable share
        dcc.Location(id="url", refresh=False),
        dcc.Store(id="memory-output"),
        dcc.Store(id="screen-width-store"),
        # Hidden div to listen
        html.Div(id="resize-listener", style={"display": "none"}),
        # Start actual layout
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
            opened=not config("DEBUG", cast=bool, default=False),
        ),
        # Header
        html.Header(
            children=[
                html.Div(
                    children=[
                        dmc.Burger(
                            color="white",
                            id="filter-button",
                            opened=False,
                            className="filterBurger",
                        ),
                        # Title or logo on the left
                        html.H1(
                            children=[
                                html.Img(
                                    src="/assets/favicon.png",
                                    style={
                                        "margin": "auto",
                                        "height": "1.15em",
                                        "paddingBottom": "0.2em",
                                        "paddingRight": "0.2em",
                                    },
                                ),
                                "PokéTactician",
                            ],
                            style={
                                "color": "#F7CE46",
                                "textAlign": "left",
                                "textShadow": "-1px 1px 0 #000,1px 1px 0 #000,1px -1px 0 #000,-1px -1px 0 #000;",
                                "animation": "glow 1s ease-in-out infinite alternate",
                            },
                        ),
                        # Navigation links on the right
                        html.Div(
                            children=[
                                html.A(
                                    DashIconify(
                                        icon="bi:envelope-at",
                                    ),
                                    href="mailto:felipe.forerome@gmail.com",
                                    style={"color": "white", "fontSize": "1.5em"},
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
                ),
            ],
            style={
                "backgroundColor": "#3E65AB",
                "padding": "10px",
            },
        ),
        # Main content flex container
        html.Div(
            style={
                "display": "flex",
            },
            children=[
                # NavBar for filters
                dmc.Navbar(
                    p="md",
                    id="navbar-container",
                    width={"base": 300},
                    fixed=False,
                    children=navbar_filter_components,
                ),
                dmc.Drawer(
                    title="",
                    id="filter-drawer",
                    padding="md",
                    zIndex=10000,
                    opened=False,
                    children=dmc.ScrollArea(
                        offsetScrollbars=True,
                        type="scroll",
                        style={"height": "85vh"},
                        children=drawer_filter_components,
                    ),
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
                                html.Div(
                                    id="team-output",
                                ),
                                html.Div(
                                    id="blank-team-output",
                                ),
                                html.Br(),
                                html.Div(style={"display": "none"}, id="placeholder"),
                            ],
                            delay_show=100,
                            overlay_style={
                                "visibility": "visible",
                                "opacity": 0.25,
                                "backgroundColor": "white",
                            },
                            type="default",
                        ),
                    ],
                ),
            ],
        ),
        # dmc.Footer(
        #     height=60,
        #     fixed=False,
        #     children=[
        #         dmc.Center(
        #             children=[
        #                 dmc.Text("Made by Felipe Forero Meola"),
        #             ]
        #         ),
        #         dmc.Center(
        #             children=[
        #                 html.Br(),
        #                 dmc.Text("Pokémon is © of Nintendo"),
        #             ]
        #         ),
        #     ],
        #     style={"color": "grey"},
        # ),
    ]
)
