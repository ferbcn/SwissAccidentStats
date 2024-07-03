import json
import time

import dash
import pandas as pd
from dash import html, dcc, dash_table, Input, Output
from plotly import express as px
# import plotly.graph_objects as go
import dash_bootstrap_components as dbc

from mongo_data_layer import MongoClient

_TITLE = "Unfälle mit Personenschäden Schweiz 2011-2023"

mc = MongoClient("unfaelle-schweiz-stats")

# Use a Bootstrap and custom CSS
external_stylesheets = [dbc.themes.CYBORG, 'assets/style.css']

app = dash.Dash(__name__, title=_TITLE, requests_pathname_prefix='/anim/', external_stylesheets=external_stylesheets)

# Create the table style
table_style = {'backgroundColor': 'transparent', 'color': 'lightgray', 'textAlign': 'left',
               'border': '1px solid lightgray', 'font_size': '10px'}

# Create the table header style
table_header_style = {'backgroundColor': 'transparent', 'color': 'lightgray', 'textAlign': 'left',
                      'fontWeight': 'bold'}

custom_colors = {
    "Unfall mit Leichtverletzten": "LightBlue",
    "Unfall mit Schwerverletzten": "Gold",
    "Unfall mit Getöteten": "Crimson"
}

ddown_options = [{"label": "Fussgänger", "value": "pedestrianYearly"},
                 {"label": "Velos", "value": "bikesYearly"},
                 {"label": "All", "value": "allYearly"},]

app.layout = html.Div([
    html.H3([
        "📊 ", _TITLE,
        html.A(html.Button("🗺", className="btn btn-secondary"), href="/map/",
               className="header-link"),
    ]),
    dcc.Dropdown(options=ddown_options, value="allYearly", id="cat_selector", className="ddown"),
    dcc.Loading(dcc.Graph(id='graph', config={'scrollZoom': True}, style={'height': '55vh'}), type='circle'),
    dcc.Loading(dcc.Graph(id='graph-total', config={'scrollZoom': True}, style={'height': '30vh'}), type='circle'),
])

@app.callback(
    Output('graph', 'figure'),
    Output('graph-total', 'figure'),
    Input('cat_selector', 'value'),
)
def update_map(cat):
    print(f"Collecting and displaying data for year...")
    variable = 'AccidentYear'

    doc = mc.get_single_doc_from_collection("accidentStat", cat)
    counts = pd.DataFrame(doc["data"])

    print(counts.columns)
    print(counts)

    # Totals per Year
    # sum all accidents per year using columns true and false
    total_counts = counts.groupby(['AccidentSeverityCategory_de', 'AccidentYear']).sum().reset_index()
    print("Totals:")
    print(total_counts)

    # bar chart
    fig = px.bar(counts, title="", x="AccidentType_de", y="count",
                animation_frame=variable, animation_group="AccidentType_de",
                color="AccidentSeverityCategory_de", hover_name="AccidentType_de",
                custom_data=['AccidentType_de', 'AccidentSeverityCategory_de', 'count'],
                category_orders={
                     "AccidentSeverityCategory_de": ["Unfall mit Leichtverletzten", "Unfall mit Schwerverletzten",
                                                     "Unfall mit Getöteten"]},
                # text='count',
                color_discrete_map=custom_colors,
                )

    fig.update_traces(hovertemplate="Type: %{customdata[0]} "
                                    "<br>Severity: %{customdata[1]} "
                                    "<br>Count: %{customdata[2]}",
                      )

    fig.update_yaxes(range=[0, counts['count'].max() + 1000])
    fig.update_xaxes(title="")
    fig.update_layout(
        legend=dict(title="", orientation="h", y=1, x=0.5, xanchor='center', yanchor='bottom'),
        coloraxis_showscale=False,
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color='lightgray'),
        mapbox_style="open-street-map",
        margin={"r": 0, "t": 30, "l": 0, "b": 20},
    )

    fig_total = px.bar(total_counts, x='AccidentYear', y='count', title='Total Accidents',
                       color="AccidentSeverityCategory_de", hover_name="AccidentType_de",
                       text='count',
                       category_orders={
                           "AccidentSeverityCategory_de": ["Unfall mit Leichtverletzten", "Unfall mit Schwerverletzten",
                                                           "Unfall mit Getöteten"]},
                       custom_data = ['count'],
                       color_discrete_map=custom_colors,  # Add this line
                       )
    fig_total.update_layout(
        legend=dict(title="", orientation="h", y=-0.2, x=0.5, xanchor='center', yanchor='bottom'),
        coloraxis_showscale=False,
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color='lightgray'),
        mapbox_style="open-street-map",
        margin={"r": 50, "t": 50, "l": 0, "b": 20},
    )
    fig_total.update_xaxes(dtick=1, title="")
    fig_total.update_traces(textposition='outside',
                            hovertemplate=None,
                            )

    return fig, fig_total


if __name__ == '__main__':
    app.run_server(debug=True)
