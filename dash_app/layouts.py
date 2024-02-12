from dash import html, dcc

# Define the layout
layout = html.Div(
    [
        html.H1("Pokémon Team Optimizer"),
        html.Button("Suggest Team", id="suggest-team-btn"),
        dcc.Loading(
            id="loading-output",
            children=[
                html.Div(id="team-output"),
                html.Br(),
                html.Div(id="time-to-calc"),
            ],
            type="default",
        ),
    ]
)
