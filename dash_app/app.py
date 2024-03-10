from dash import Dash
import dash_bootstrap_components as dbc
from layouts import layout
import callbacks  # This imports the callbacks to register them with the app
from decouple import config

# Initialize the Dash app
app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
app.title = "PokéTactician"
server = app.server

app.layout = layout

if __name__ == "__main__":
    if config("DEBUG", False, cast=bool):
        app.run(debug=True, host="0.0.0.0", port=8080)
    else:
        from waitress import serve

        serve(server, host="0.0.0.0", port=8080)
