import json
import time

import dash
import pandas as pd
from dash import html, dcc, dash_table, Input, Output
from plotly import express as px
# import plotly.graph_objects as go
import dash_bootstrap_components as dbc

from mongo_data_layer import MongoClient

_TITLE = "Unfälle mit Fahrrädern"

mc = MongoClient("unfaelle-schweiz-stats")

# Use a Bootstrap CSS URL
external_stylesheets = [dbc.themes.CYBORG, 'assets/style.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
app.title = _TITLE

# Create the table style
table_style = {'backgroundColor': 'transparent', 'color': 'lightgray', 'textAlign': 'left',
               'border': '1px solid lightgray', 'font_size': '10px'}

# Create the table header style
table_header_style = {'backgroundColor': 'transparent', 'color': 'lightgray', 'textAlign': 'left',
                      'fontWeight': 'bold'}


app.layout = html.Div([
    html.H3(_TITLE),
    dcc.Dropdown([y for y in range(2011, 2024)], 2011, id="year_selector", style={"display": "none"}),
    dcc.Loading(dcc.Graph(id='graph', config={'scrollZoom': True}, style={'height': '55vh'}), type='circle'),
    dcc.Loading(dcc.Graph(id='graph-total', config={'scrollZoom': True}, style={'height': '30vh'}), type='circle'),
])

@app.callback(
    Output('graph', 'figure'),
    Output('graph-total', 'figure'),
    Input('year_selector', 'value'),
)
def update_map(year):
    print(f"Collecting and displaying data for year...")
    variable = 'AccidentYear'
    # convert mongo db collection to geopandas dataframe

    # counts = pd.read_json("data/bike_stats.json")
    doc = mc.get_single_doc_from_collection("accidentStat", "bikesYearly")
    counts = pd.DataFrame(doc["data"])

    print(counts.columns)
    print(counts)

    # mc.drop_collection()
    # doc_count = {"accidentStat": "bikesYearly", "data": counts.to_dict(orient="records")}
    # res = mc.insert_many_documents([doc_count])
    # print(f"Inserted {len(res.inserted_ids)} documents into MongoDB")

    # bar chart
    fig = px.bar(counts, title="Accident Categories", x="AccidentType_de", y="count",
                animation_frame=variable, animation_group="AccidentType_de",
                color="AccidentSeverityCategory_de", hover_name="AccidentType_de",
                color_discrete_map={
                "AccidentSeverityCategory_de": {"Unfall mit Getöteten": "red",
                                                "Unfall mit Schwerverletzten": "yellow",
                                                "Unfall mit Leichtverletzten": "blue",
                                                }},
                custom_data=['AccidentType_de', 'AccidentSeverityCategory_de', 'count'],
                 )

    fig.update_traces(hovertemplate="Type: %{customdata[0]} "
                                    "<br>Severity: %{customdata[1]} "
                                    "<br>Count: %{customdata[2]}",
                      )
    fig.update_yaxes(range=[0, 2500])
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

    # Totals per Year
    # sum all accidents per year using columns true and false
    total_counts = counts.groupby(['AccidentSeverityCategory_de', 'AccidentYear']).sum().reset_index()
    print("Totals:")
    print(total_counts)

    fig_total = px.bar(total_counts, x='AccidentYear', y='count', title='Total Accidents',
                       color="AccidentSeverityCategory_de", hover_name="AccidentType_de",
                       color_discrete_map={
                           "AccidentSeverityCategory_de": {"Unfall mit Getöteten": "red",
                                                           "Unfall mit Schwerverletzten": "yellow",
                                                           "Unfall mit Leichtverletzten": "blue",
                                                           }},
                       text='count',
                       )
    fig_total.update_layout(
        legend=dict(title="", orientation="h", y=-0.2, x=0.5, xanchor='center', yanchor='bottom'),
        coloraxis_showscale=False,
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color='lightgray'),
        mapbox_style="open-street-map",
        margin={"r": 0, "t": 50, "l": 0, "b": 20},
    )
    fig_total.update_xaxes(dtick=1, title="")
    fig_total.update_traces(textposition='outside')

    return fig, fig_total


if __name__ == '__main__':
    app.run_server(debug=True)
