import dash
import geopandas as gpd
from dash import html, dcc, dash_table, Input, Output
from plotly import express as px
import plotly.graph_objects as go
import dash_bootstrap_components as dbc

# Use a Bootstrap CSS URL
external_stylesheets = [dbc.themes.CYBORG, 'assets/style.css']

# filepath = 'data/unfaelle-personenschaeden_alle_4326.json/RoadTrafficAccidentLocations.json'
#filepath = 'data/unfaelle_small_1000.geojson'  # small sample file

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)


def get_data(year):
    # filepath = 'data/unfaelle_small_1000.geojson'
    filepath = f"data/unfaelle_{year}.geojson"
    print(f"Reading file {filepath}...")
    return gpd.read_file(filepath)


def generate_pie(labels, values):
    fig = go.Figure(go.Pie(labels=labels, values=values,
                               textinfo='label+percent',
                               insidetextorientation='radial',
                               hole=0.3,
                               marker=dict(colors=px.colors.qualitative.Plotly),
                               ))
    fig.update_layout(title_font={'size': 12, 'color': 'lightgray'},
                          paper_bgcolor='rgba(0,0,0,0)',
                          font=dict(color='lightgray'),
                          autosize=True,
                          margin=dict(l=0, r=0, t=0, b=0),
                          )
    return fig


app.layout = html.Div([
    html.H3("Unfälle mit Personenschäden Schweiz"),
    html.Div(["Jahr: ", dcc.Dropdown(value=2023,
                                     id="year_selector",
                                     options=[{"label": x, "value": x} for x in range(2011, 2024)], className="ddown")],
             className="ddown-container"),
    dcc.Loading(dcc.Graph(id='map', config={'scrollZoom': True}, style={'height': '60vh'}), type='circle'),

    html.Div([
        dash_table.DataTable(id='table-severity'),
        dcc.Loading(dcc.Graph(id="graph-pie-severity"), type="graph"),
        ], className="table-pie-container"),

    html.Div([
        dash_table.DataTable(id='table'),
        dcc.Loading(dcc.Graph(id="graph-pie"), type="graph"),
        ], className="table-pie-container"),

    ])

@app.callback(
    Output('map', 'figure'),
    Output('table-severity', 'columns'),
    Output('table-severity', 'data'),
    Output("table-severity", "style_data"),
    Output("table-severity", "style_header"),
    Output("graph-pie-severity", "figure"),
    Output('table', 'columns'),
    Output('table', 'data'),
    Output("table", "style_data"),
    Output("table", "style_header"),
    Output("graph-pie", "figure"),
    Input('year_selector', 'value')
)
def update_map(year):
    gdf = get_data(year)
    print(gdf.shape)
    print(gdf.columns)

    # sum total number of accidents by AccidentType
    counts = gdf['AccidentType_de'].value_counts()
    counts_severity = gdf['AccidentSeverityCategory_de'].value_counts()
    # print(gdf['AccidentType_de'].value_counts())
    # print(gdf['AccidentSeverityCategory_de'].value_counts())
    # print(gdf['RoadType_de'].value_counts())

    fig = px.density_mapbox(gdf, lat=gdf['geometry'].y, lon=gdf['geometry'].x, radius=10,
                            color_continuous_scale="inferno",
                            )
    fig.update_layout(
        coloraxis_showscale=False,
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color='lightgray'),
        mapbox_style="open-street-map",
        margin={"r": 0, "t": 10, "l": 0, "b": 20},
    )

    columns = [{"name": "Unfallart Type", "id": "type"}, {"name": "count", "id": "count"}]
    # convert counts to a dictionary for the table_data
    table_data = [{"type": k, "count": v} for k, v in counts.items()]
    labels = [k for k in counts.keys()]
    values = [v for v in counts.values]

    fig_pie = generate_pie(labels, values)

    columns_severity = [{"name": "Unfallschwere", "id": "severity"}, {"name": "count", "id": "count"}]
    # convert counts to a dictionary for the table_data
    table_data_severity = [{"severity": k, "count": v} for k, v in counts_severity.items()]
    labels_severity = [k for k in counts_severity.keys()]
    values_severity = [v for v in counts_severity.values]

    fig_pie_severity = generate_pie(labels_severity, values_severity)

    # Create the table style
    table_style = {'backgroundColor': 'transparent', 'color': 'lightgray', 'textAlign': 'left',
                   'border': '1px solid lightgray'}

    # Create the table header style
    table_header_style = {'backgroundColor': 'transparent', 'color': 'lightgray', 'textAlign': 'left',
                          'fontWeight': 'bold'}

    return (fig, columns_severity, table_data_severity, table_style, table_header_style, fig_pie_severity,
            columns, table_data, table_style, table_header_style, fig_pie)


if __name__ == '__main__':
    app.run_server(debug=True)
