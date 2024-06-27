import time
import dash
import pandas as pd
from dash import html, dcc, Input, Output, State
from plotly import express as px
import plotly.graph_objects as go
import dash_bootstrap_components as dbc

from mongo_data_layer import MongoClient

_TITLE = "Unfälle mit Personenschäden Schweiz 2011-2023"

mc = MongoClient("unfaelle-schweiz")

# Use a Bootstrap CSS URL
external_stylesheets = [dbc.themes.CYBORG, 'assets/style.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets, title=_TITLE, requests_pathname_prefix='/map/')

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


def generate_chart(labels, values, graph_type="Bar", severity=False):
    if severity:
        colors = list(custom_colors.values())
    else:
        colors = px.colors.qualitative.Plotly
    if graph_type == "Pie":
        fig = go.Figure(go.Pie(labels=labels, values=values,
                               textinfo='label+percent',
                               insidetextorientation='radial',
                               hole=0.3,
                               marker=dict(colors=colors),
                               ))
    else:
        fig = go.Figure(go.Bar(x=labels, y=values, text=values, textposition='outside',
                               marker=dict(color=colors),
                               ))

    fig.update_layout(title_font={'size': 12, 'color': 'lightgray'},
                      plot_bgcolor='rgba(0,0,0,0)',
                      paper_bgcolor='rgba(0,0,0,0)',
                      font=dict(color='lightgray'),
                      autosize=True,
                      margin=dict(l=30, r=30, t=10, b=50),
                      height=400,
                      )
    return fig


app.layout = html.Div([

    dbc.Modal(
        [
            dbc.ModalHeader("Notice"),
            dbc.ModalBody("You have selected a very large dataset, expect longer loading time!"),
            dbc.ModalFooter(
                dbc.Button("Close", id="close", className="ml-auto")
            ),
        ],
        id="modal",
    ),

    html.H3([
        _TITLE,
        html.A("📊", href="/anim/", className="header-link")
    ]),
    html.Div([
        html.Div([
            "Jahr: ", dcc.Dropdown(value="2023",
                                   id="year_selector",
                                   options=ddown_options, className="ddown"),
        ], className='ddown-box'),
        html.Div([
            "Typen/Schwere: ", dcc.Dropdown(
                value="AccidentType_de",
                id="class_selector",
                options=[{"label": "Types", "value": "AccidentType_de"},
                         {"label": "Severity", "value": "AccidentSeverityCategory_de"}], className="ddown")
        ], className='ddown-box'),
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
        dcc.Loading(dcc.Graph(id="graph-pie"), type="circle"),
        dcc.Loading(dcc.Graph(id="graph-bar"), type="circle"),
    ], className="chart-container"),
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

    # reformat geometry and properties columns
    init = time.time()
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
                            # reorder x-axis
                            category_orders={"AccidentSeverityCategory_de": ["Unfall mit Leichtverletzten",
                                                                             "Unfall mit Schwerverletzten",
                                                                             "Unfall mit Getöteten"]},
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
        labels = [k for k in counts.keys()]
        values = [v for v in counts.values]

    else:
        labels = [k for k in counts_severity.keys()]
        values = [v for v in counts_severity.values]

    if class_type == "AccidentSeverityCategory_de":
        severity = True
    else:
        severity = False

    fig_pie = generate_chart(labels, values, "Pie", severity=severity)  # Always generate the pie chart
    fig_bar = generate_chart(labels, values, "Bar", severity=severity)  # Always generate the bar chart

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
