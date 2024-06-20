import dash
from dash import html, dcc, Input, Output, dash_table
from plotly import express as px
import plotly.graph_objects as go
import dash_bootstrap_components as dbc
import pandas as pd
from plotly.subplots import make_subplots

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
    filepath = "data/stats_all.json"
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
    # Add column "Total" to sum up all values of bike_false and bike_true
    df["Total"] = df["bikes_false"] + df["bikes_true"]

    print(df.columns)
    print(df.head())

    # Create a subplot for the bar chart and another for the line plots
    fig = make_subplots(specs=[[{"secondary_y": True}]])

    # Add line plot for each column except "Total" to the second subplot
    for column in df.columns[1:-1]:  # Exclude "Total" from the line plot
        fig.add_trace(
            go.Scatter(
                x=df["year"],
                y=df[column],
                mode='lines',
                name=column,
            ),
            secondary_y=True,
        )

    # Add bar chart for "Total" to the first subplot
    fig.add_trace(
        go.Bar(
            x=df["year"],
            y=df["Total"],
            name="Total",
            marker=dict(color='darkgray'),
        ),
        secondary_y=False,
    )

    fig.update_layout(
        # position legend below plot
        legend=dict(orientation="h", y=-0.8, x=0.5, xanchor='center', yanchor='bottom'),
        plot_bgcolor='dimgray',
        coloraxis_showscale=False,
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color='lightgray'),
        margin={"r": 0, "t": 30, "l": 0, "b": 20},
        yaxis2=dict(  # Add a second y-axis
            title="Total",
            overlaying="y",
            side="right",
        ),
    )
    fig.update_xaxes(dtick=1)
    return fig


if __name__ == '__main__':
    app.run_server(debug=True)


