from dash import html, dcc
import dash_mantine_components as dmc

from dash_iconify import DashIconify

# Define the layout
layout = html.Div(
    children=[
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
                                    "About",
                                    href="/about",
                                    style={"marginRight": "15px", "color": "white"},
                                ),
                                html.A(
                                    "Contact", href="/contact", style={"color": "white"}
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
                            label="Select Types to Exclude",
                            placeholder="None",
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
                    style={"flexGrow": 1, "marginLeft": 20, "overflow": "auto"},
                    children=[
                        dcc.Loading(
                            id="loading-output",
                            children=[
                                html.Br(),
                                html.Div(id="team-output"),
                                html.Br(),
                                html.Div(id="time-to-calc"),
                            ],
                            type="default",
                        ),
                    ],
                ),
            ],
        ),
    ]
)
