import time

import dash
import pandas as pd
from dash import html, dcc, dash_table, Input, Output, State
from plotly import express as px
import plotly.graph_objects as go
import dash_bootstrap_components as dbc


from mongo_data_layer import MongoClient

_TITLE = "Unfälle mit Personenschäden Schweiz 2011-2023"

mc = MongoClient("unfaelle-schweiz")

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

custom_colors = {
    "Unfall mit Leichtverletzten": "Lightgreen",
    "Unfall mit Schwerverletzten": "Gold",
    "Unfall mit Getöteten": "Crimson"
}

ddown_options = [{"label": x, "value": str(x)} for x in range(2011, 2024)]
ddown_options.append({"label": "All", "value": "all"})


def generate_chart(labels, values, graph_type="Bar"):
    if graph_type == "Pie":
        fig = go.Figure(go.Pie(labels=labels, values=values,
                               textinfo='label+percent',
                               insidetextorientation='radial',
                               hole=0.3,
                               marker=dict(colors=px.colors.qualitative.Plotly),
                               ))
    else:
        fig = go.Figure(go.Bar(x=labels, y=values, text=values, textposition='outside',
                               marker=dict(color=px.colors.qualitative.Plotly)))

    fig.update_layout(title_font={'size': 12, 'color': 'lightgray'},
                      plot_bgcolor='rgba(0,0,0,0)',
                      paper_bgcolor='rgba(0,0,0,0)',
                      font=dict(color='lightgray'),
                      autosize=True,
                      margin=dict(l=0, r=0, t=10, b=50),
                      )
    return fig


app.layout = html.Div([

    dbc.Modal(
        [
            dbc.ModalHeader("Notice"),
            dbc.ModalBody("Long loading time!"),
            dbc.ModalFooter(
                dbc.Button("Close", id="close", className="ml-auto")
            ),
        ],
        id="modal",
    ),

    html.H3(_TITLE),
    html.Div([
        html.Div([
            "Jahr: ", dcc.Dropdown(value="2023",
                                   id="year_selector",
                                   options=ddown_options, className="ddown"),
        ], className='ddown'),
        html.Div([
            "Classification: ", dcc.Dropdown(
                value="AccidentType_de",
                id="class_selector",
                options=[{"label": "Types", "value": "AccidentType_de"},
                         {"label": "Severity", "value": "AccidentSeverityCategory_de"}], className="ddown")
        ], className='ddown'),
    ], className="ddown-container"),

    dcc.Loading(dcc.Graph(id='map', config={'scrollZoom': True}, style={'height': '55vh'}), type='circle'),

    dcc.RadioItems(
        id='graph-type',
        options=[{'label': i, 'value': i} for i in ['Bar', 'Pie']],
        value='Bar',
        labelStyle={'display': 'inline-block', 'margin': '10px'},
        style={'color': 'lightgray', 'textAlign': 'right'}
    ),

    html.Div([
        # dash_table.DataTable(id='table', style_cell=table_style, style_header=table_header_style),
        dcc.Loading(dcc.Graph(id="graph-pie"), type="circle"),
        dcc.Loading(dcc.Graph(id="graph-bar"), type="circle"),
    ], className="table-pie-container"),
    html.Div([
        html.Pre(children="Source: FEDRO - Federal Roads Office"),
        html.A(
            children='Data',
            href='https://data.geo.admin.ch/browser/index.html#/collections/ch.astra.unfaelle-personenschaeden_alle',
            target='_blank',  # This makes the link open in a new tab
            className='source-link'
        )
    ], className='source-data')
])


@app.callback(
    Output('map', 'figure'),
    # Output('table', 'columns'),
    # Output('table', 'data'),
    Output("graph-pie", "figure"),
    Output("graph-bar", "figure"),  # New output for the bar chart
    Input('year_selector', 'value'),
    Input('class_selector', 'value'),
)
def update_map(year, class_type):
    print(f"Collecting and displaying data for year {year}...")
    # convert mongo db collection to geopandas dataframe
    init = time.time()
    if year == "all":
        docs = mc.get_all_docs_from_collection()
    else:
        docs = mc.get_docs_from_collection("properties.AccidentYear", str(year))

    gdf = pd.DataFrame(docs)
    print(f"Time to fetch data from MongodDB and convert to GeoDataFrame: {time.time() - init:.2f} seconds")

    init = time.time()
    # # reformat geometry and properties columns
    # df = pd.DataFrame.from_records(gdf['properties'].tolist())
    # df_geo = pd.DataFrame.from_records(gdf['geometry'].tolist())
    # df_geo = pd.DataFrame.from_records(df_geo['coordinates'].tolist())
    # df_geo.rename(columns={1: "lat", 0: "lon"}, inplace=True)

    # reformat geometry and properties columns
    df = pd.DataFrame([x for x in gdf['properties'].tolist() if x is not None and hasattr(x, '__iter__')])
    df_geo = pd.DataFrame.from_records([x for x in gdf['geometry'].tolist() if x is not None and hasattr(x, '__iter__')])
    df_geo = pd.DataFrame.from_records([x for x in df_geo['coordinates'].tolist() if x is not None and hasattr(x, '__iter__')])
    df_geo.rename(columns={1: "lat", 0: "lon"}, inplace=True)

    # combine the two dataframes
    gdf = pd.concat([df, df_geo], axis=1)
    print(f"Time to convert to DataFrame: {time.time() - init:.2f} seconds")

    # sum total number of accidents by AccidentType
    counts = gdf['AccidentType_de'].value_counts()
    counts_severity = gdf['AccidentSeverityCategory_de'].value_counts()

    fig = px.scatter_mapbox(gdf, lat='lat', lon='lon',
                            color=class_type,
                            zoom=7,
                            size=[5]*len(gdf),
                            mapbox_style="open-street-map",
                            color_continuous_scale="inferno",
                            hover_data=['AccidentType_de', 'AccidentSeverityCategory_de', 'AccidentInvolvingBicycle'],
                            color_discrete_map=custom_colors,
                            )

    fig.update_traces(hovertemplate="Type: %{customdata[0]} "
                                    "<br>Severity: %{customdata[1]} "
                                    "<br>Coordinates: %{lat}, %{lon}",
                      )

    fig.update_layout(
        legend=dict(title="", orientation="h", y=-0.1, x=0.5, xanchor='center', yanchor='bottom'),
        coloraxis_showscale=False,
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color='lightgray'),
        mapbox_style="open-street-map",
        margin={"r": 0, "t": 20, "l": 0, "b": 20},
    )

    if class_type == "AccidentType_de":
        # columns = [{"name": "Unfallart Type", "id": "type"}, {"name": "count", "id": "count"}]
        # # convert counts to a dictionary for the table_data
        # table_data = [{"type": k, "count": v} for k, v in counts.items()]
        labels = [k for k in counts.keys()]
        values = [v for v in counts.values]

    else:
        # columns = [{"name": "Unfallschwere", "id": "severity"}, {"name": "count", "id": "count"}]
        # # convert counts to a dictionary for the table_data
        # table_data = [{"severity": k, "count": v} for k, v in counts_severity.items()]
        labels = [k for k in counts_severity.keys()]
        values = [v for v in counts_severity.values]

    fig_pie = generate_chart(labels, values, "Pie")  # Always generate the pie chart
    fig_bar = generate_chart(labels, values, "Bar")  # Always generate the bar chart

    # return fig, columns, table_data, fig_pie, fig_bar  # Return both charts
    return fig, fig_pie, fig_bar  # Return both charts


@app.callback(
    Output('graph-pie', 'style'),
    Output('graph-bar', 'style'),
    Input('graph-type', 'value')
)
def toggle_graphs(graph_type):
    if graph_type == 'Pie':
        return {'display': 'block'}, {'display': 'none'}
    else:
        return {'display': 'none'}, {'display': 'block'}


# Add this callback to your callbacks
@app.callback(
    Output("modal", "is_open"),
    [Input("year_selector", "value"),
     Input("close", "n_clicks")],
    [State("modal", "is_open")],
)
def toggle_modal(year, n, is_open):
    if year == "all" or n:
        return not is_open
    else:
        return False


if __name__ == '__main__':
    app.run_server(debug=True)
