

import dash
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
import plotly.express as px
import psycopg2
import plotly.graph_objs as go
from datetime import datetime as dt
import re
from dash.dependencies import Input, Output, State

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
#external_stylesheets = ['https://github.com/STATWORX/blog/blob/master/DashApp/assets/style.css']

app = dash.Dash(__name__,external_stylesheets=external_stylesheets)

# Connect to postgreSQL database
pgconnect = psycopg2.connect(\
    host = '***', \
    port = ***,
    database = '***',
    user = '***',
    password = "***")
pgcursor = pgconnect.cursor()

# ------------------------------------------------------------------------------
# Import and clean data from postgres
#df_gdp = pd.read_csv('https://stats.oecd.org/sdmx-json/data/DP_LIVE/.QGDP.TOT.PC_CHGPP.Q/OECD?contentType=csv&detail=code&separator=comma&csv-lang=en&startPeriod=2018-Q4&endPeriod=2020-Q2', usecols = ['LOCATION','TIME','Value'])
#df_ir = pd.read_csv('https://stats.oecd.org/sdmx-json/data/DP_LIVE/.STINT.TOT.PC_PA.M/OECD?contentType=csv&detail=code&separator=comma&csv-lang=en&startPeriod=1956-01&endPeriod=2020-09', usecols = ['LOCATION', 'TIME', 'Value'])

# Grab forex data table
pgcursor.execute("SELECT * FROM fx_data ORDER BY pair,date")
fx_df = pd.DataFrame(pgcursor.fetchall(),
    columns=['pair', 'date', 'min_bid', 'max_bid', 'avg_bid', 
             'min_ask', 'max_ask', 'avg_ask'])
#df.index = pd.to_datetime(df['Date'])

#fx_df = fx_df.groupby(['pair','date'])
print(fx_df)
fx_df.index = pd.to_datetime(fx_df['date'])

# Grab interest rate table
pgcursor.execute("SELECT * FROM ir_data")
ir_df = pd.DataFrame(pgcursor.fetchall(),
    columns=['location', 'date', 'value'])
print(ir_df)

# Upload currency to country conversion
cc_file = 'data/country_code.csv'
cc_df = pd.read_csv(cc_file)
print(cc_df.head(5))


def get_options(list_pairs):
    dict_list = []
    for i in list_pairs:
        dict_list.append({'label': i, 'value': i})
    return dict_list

def first_ask_bid(currency_pair, t):
    t = t.replace(year=2016, month=1, day=5)
    items = currency_pair_data[currency_pair]
    dates = items.index.to_pydatetime()
    index = min(dates, key=lambda x: abs(x - t))
    df_row = items.loc[index]
    int_index = items.index.get_loc(index)
    return [df_row, int_index]  # returns dataset row and index of row

# -------------------------------- Layout --------------------------------------
#html.Div(style={'fontColor': 'blue'}, children=dcc.Dropdown(...))

app.layout = html.Div(
    children=[
    html.Div(className='row',
        children=[
        dcc.Interval(id="i_tris", interval=1 * 5000, n_intervals=0),
        # Left Column
        html.Div(className='four columns div-user-controls',
            children=[
            html.H2('Forex Flow'),
            html.P('Visualising Forex price action with interest rate changes.'),
            html.P('Pick a currency pair and timeframe from the dropdown below:'),
            html.Div(className='div-for-dropdown',
                children=[
                    dcc.Dropdown(
                        id='pairselector', 
                        options=get_options(fx_df['pair'].unique()), 
                        multi=True,
                        value=[fx_df['pair'].sort_values()[0]],
                        placeholder="Select currency pair...",
                        style={'backgroundColor': '#1E1E1E'},
                        className='pairselector'
                    ),
                    dcc.RadioItems(
                        id='year_radio',
                        className= "dropdown_period",
                        options=[
                            {'label': '3 Months', 'value': '3Month'},
                            {'label': '6 Months', 'value': '6Month'},
                            {'label': '1 Year', 'value': '1Year'},
                            {'label': '2 Year', 'value': '2Year'},
                            {'label': '5 Year', 'value': '5Year'},
                            {'label': '10 Year', 'value': '10Year'}],
                        value='1Year',
                    ),
                    html.Div(id='year_dropdown'),
                ],
               style={'color': 'white'}),

            ]
        ),
        # Right Column
        html.Div(
            className='eight columns div-for-charts bg-grey',
            children=[
            dcc.Graph(
                id='timeseries', 
                config={'displayModeBar': False}, 
                animate=True),
            dcc.Graph(
                id='interestseries', 
                config={'displayModeBar': False}, 
                animate=True)
           ])
       ])
    ]

)


# ------------------------------ Callback --------------------------------------
# Dropdown Currency Pair
@app.callback(
    dash.dependencies.Output('pd_dropdown_container', 'children'),
    [dash.dependencies.Input('pair_dropdown', 'value')])
def update_output(value):
    return 'You have selected "{}"'.format(value)

# # Radiobutton Year 
# @app.callback(
#     dash.dependencies.Output('year_dropdown', 'children'),
#     [dash.dependencies.Input('year_radio', 'value')])
# def update_output(value):
#     return 'You have selected "{}"'.format(value)

# @app.callback(
#     Output(pair + "chart", "figure"),
#     [
#         Input("i_tris", "n_intervals"),
#         Input(pair + "dropdown_period", "value"),
#     ],
#     [
#         State(pair + "ask", "children"),
#         State(pair + "bid", "children"),
#         State(pair + "chart", "figure"),
#     ],
#     )(generate_figure_callback(pair))

# Callback for timeseries price chart
@app.callback(
    Output('timeseries', 'figure'),
    [Input('pairselector', 'value')])
def update_graph(pair):
    trace1 = []
    #pair = selected_dropdown_value
    for p in pair:
        trace1.append(
            go.Scatter(
                x=fx_df[fx_df['pair'] == p].index,
                y=fx_df[fx_df['pair'] == p]['avg_bid'],
                mode='lines',
                opacity=0.7,
                name=p,
                textposition='bottom center'))
        traces = [trace1]
        data = [val for sublist in traces for val in sublist]
        figure = {'data': data,
        'layout': go.Layout(
            colorway=["#5E0DAC", '#FF4F00', '#375CB1', '#FF7400', '#FFF400', '#FF0056'],
            template='plotly_white',
            paper_bgcolor='rgba(0, 0, 0, 0)',
            plot_bgcolor='rgba(0, 0, 0, 0)',
            margin={'b': 15},
            hovermode='x',
            autosize=True,
            title={'text': 'Currency Pair Price Action', 'font': {'color': 'black'}, 'x': 0.5},
            xaxis={'showticklabels': True,'range': [fx_df.index.min(), fx_df.index.max()]},
            ),
        }
    return figure

@app.callback(
    Output('interestseries', 'figure'),
    [Input('pairselector', 'value')])
def update_graph(pair):
    trace1 = []
    #pair = selected_dropdown_value
    for p in pair:
        trace1.append(
            go.Scatter(
                x=fx_df[fx_df['pair'] == p].index,
                y=fx_df[fx_df['pair'] == p]['avg_bid'],
                mode='lines',
                opacity=0.7,
                name=p,
                textposition='bottom center'))
        traces = [trace1]
        data = [val for sublist in traces for val in sublist]
        figure = {'data': data,
        'layout': go.Layout(
            colorway=["#5E0DAC", '#FF4F00', '#375CB1', '#FF7400', '#FFF400', '#FF0056'],
            template='plotly_white',
            paper_bgcolor='rgba(0, 0, 0, 0)',
            plot_bgcolor='rgba(0, 0, 0, 0)',
            margin={'b': 15},
            hovermode='x',
            autosize=True,
            title={'text': 'Currency Pair Price Action', 'font': {'color': 'black'}, 'x': 0.5},
            xaxis={'showticklabels': True,'range': [fx_df.index.min(), fx_df.index.max()]},
            ),
        }
    return figure

# Callback to update live clock
@app.callback(Output("live_clock", "children"), [Input("interval", "n_intervals")])
def update_time(n):
    return datetime.datetime.now().strftime("%H:%M:%S")

# ------------------------------ End Callback ----------------------------------
if __name__ == '__main__':
    app.run_server(debug=True, port=8050, host="ec2-3-101-124-56.us-west-1.compute.amazonaws.com")
    