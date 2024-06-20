import json
import dash
import geopandas as gpd
from dash import html, dcc, dash_table, Input, Output
from plotly import express as px
import plotly.graph_objects as go
import dash_bootstrap_components as dbc
import pandas as pd

# Use a Bootstrap CSS URL
external_stylesheets = [dbc.themes.CYBORG, 'assets/style.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)


app.layout = html.Div([
    html.H4("Unfälle mit Personenschäden Schweiz 2012-2023"),
    dcc.Dropdown([], "", id="year_selector", style={"display": "none"}),
    dcc.Loading(dcc.Graph(id='chart', config={'scrollZoom': True}, style={'height': '60vh'}), type='circle'),

    ])

@app.callback(
    Output('chart', 'figure'),
    Input('year_selector', 'value')
)
def update_map(year):
    filepath = "stats_all.json"
    df = pd.read_json(filepath)
    print(df.columns)
    print(df.head())

    # Iterate through each column except the first one
    for column in df.columns[1:]:
        # Expand the JSON data into separate columns
        expanded_df = df[column].apply(pd.Series)
        # Rename the new columns to include the original column name as a prefix
        expanded_df = expanded_df.add_prefix(f'{column}_')
        # Drop the original column
        df = df.drop(columns=[column])
        # Concatenate the new columns with the original DataFrame
        df = pd.concat([df, expanded_df], axis=1)

    print(df.columns)
    print(df.head())

    fig = px.line(df, x="year", y=df.columns[1:])
    fig.update_layout(
        plot_bgcolor='lightgray',
        coloraxis_showscale=False,
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color='lightgray'),
        margin={"r": 0, "t": 30, "l": 0, "b": 20},
    )
    fig.update_xaxes(dtick=1)
    return fig


if __name__ == '__main__':
    app.run_server(debug=True)
