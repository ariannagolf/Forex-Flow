

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
import time

#print('Start of New Session')

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__,external_stylesheets=external_stylesheets,suppress_callback_exceptions=True)

# Connect to postgreSQL database
pgconnect = psycopg2.connect(\
    host = '***', \
    port = ***,
    database = '***',
    user = '***',
    password = '***')
pgcursor = pgconnect.cursor()

# ------------------------ Import Data -------------------------------

# Load forex data table
pgcursor.execute('SELECT * FROM fx_data ORDER BY pair,date')
fx_df = pd.DataFrame(pgcursor.fetchall(),
    columns=['pair', 'date', 'min_bid', 'max_bid', 'avg_bid', 
             'min_ask', 'max_ask', 'avg_ask'])

# Index forex data by time
fx_df.index = pd.to_datetime(fx_df['date'],format='%Y%m%d', errors='ignore')
#fx_dates = pd.to_datetime(fx_df['date'],format='%Y%m', errors='ignore')

# Load interest rate table
pgcursor.execute('SELECT * FROM ir_data')
ir_df = pd.DataFrame(pgcursor.fetchall(),columns=['location', 'value', 'date'])

# Index interest rate data by date
ir_df.index = pd.to_datetime(ir_df['date'])

# Define the Date Range
date_range = pd.date_range(start=fx_df.index.min(), end=fx_df.index.max())

# Upload country code conversion spreadsheet
cc_file = 'data/country_code.csv'
cc_df = pd.read_csv(cc_file)

# -------------------------------------------------------

def get_currency_options(list_pairs):
    """ Return list of unique currency pairs  """
    dict_list = []
    for i in list_pairs:
        dict_list.append({'label': i, 'value': i})
    return dict_list

def get_country_options(list_pairs):
    """ Return countries from cc_file """
    dict_list = []
    for i in list_pairs:
        dict_list.append({'label': i, 'value': i})
    return dict_list

def country_from_pair(pair):
    """ Separate currency pair and convert to countries """
    b = pair[:3]
    q = pair[-3:]
    base = cc_df.loc[cc_df['currency'] == b]['country'].values[0]
    quote = cc_df.loc[cc_df['currency'] == q]['country'].values[0]
    return base,quote

def country_code_from_pair(pair):
    """ 
    Separate currency pair and convert to country code:
        EURUSD -> (EA19, USA)
    """
    b = pair[:3]
    q = pair[-3:]
    base = cc_df.loc[cc_df['currency'] == b]['code'].values[0]
    quote = cc_df.loc[cc_df['currency'] == q]['code'].values[0]
    return base,quote

def currency_from_country(country):
    """ 
    Converts country to currency: 
        USA -> USD 
    """
    currency = cc_df.loc[cc_df['country'] == country]['currency'].values[0]
    return currency

def code_from_country(country):
    """ 
    Converts country to currency: 
        USA -> US 
    """
    code = cc_df.loc[cc_df['country'] == country]['code'].values[0]
    return code

def relevant_pairs(country):
    """
    Find the pairs that correspond to a given country:
        EA19 -> ('EURAUD','EURCHF','EURGBP','EURJPY','EURUSD'0)
    """
    lst = fx_df['pair'].unique()
    pairs = []
    for i in lst:
        if currency_from_country(country) == i[:3] or currency_from_country(country) == i[-3:]:
            pairs.append(i)
    return pairs

def map_values(country):
    """
    Extract 1 months worth of data from relevant pairs and create
    dataframe to populate Map
    """
    lst = relevant_pairs(country)
    pair_dict = {}
    d_country = []
    d_state = []
    d_country_code = []
    # Add user chosen country as the anchor key to pair_dict
    d_country.append(country)
    d_state.append('key')
    d_country_code.append(code_from_country(country))
    for pair in lst:
        # Define date range to be 30 days
        start = date_range[-10]
        end = date_range[-40]
        # Compute average values for given date range
        start_ask = fx_df[(fx_df['date'] == start) & (fx_df['pair'] == 'AUDCAD')]['avg_bid'][0]
        end_ask = fx_df[(fx_df['date'] == end) & (fx_df['pair'] == pair)]['avg_bid'][0]
        base,quote = country_from_pair(pair)
        # When the net change change in price is positive 
        if end_ask - start_ask > 0:
            if quote == country:
                d_country.append(base)
                d_state.append('increase')
                d_country_code.append(code_from_country(base))
            else:
                d_country.append(quote)
                d_state.append('decrease')
                d_country_code.append(code_from_country(quote))
        # When the net change change in price is negative
        else:
            if quote == country:
                d_country.append(base)
                d_state.append('decrease')
                d_country_code.append(code_from_country(base))
            else:
                d_country.append(quote)
                d_state.append('increase')
                d_country_code.append(code_from_country(quote))
    pair_dict['country'] = d_country
    pair_dict['state'] = d_state
    pair_dict['code'] = d_country_code
    # Create dataframe from data
    df = pd.DataFrame(pair_dict, columns = ['country', 'state','code'])
    return df



# ------------------------------ Layout ----------------------------------
# Create a Dash layout
app.layout = html.Div([
    dcc.Tabs(id='tabs', value='Tab1', children=[
        dcc.Tab(label='Charts', id='tab1', value='Tab1', children =[
        ]),
        dcc.Tab(label='Map', id='tab2', value='Tab2', children=[
        ])
    ],
    colors={
            "border": "black",
            "primary": "black",
            "background": "black",
            }
    )
])

# ------------------------------ Callbacks ---------------------------------
# Contents for Chart Tab
@app.callback(Output('tab1', 'children'),
              [Input('tabs', 'value')])
def update_tabs(value):
    """ Establish Layout for charts tab """
    if value == 'Tab1':
        return html.Div(
            className='row',
                children=[
                    # Left Column
                    html.Div(className='four columns div-user-controls',
                        children=[
                            html.H2('Currency Flow'),
                            html.P('Visualizing Forex price action with interest rate changes.'),
                            html.P('Pick a currency pair from the dropdown below and the daily price action and corresponding interest rate data will be displayed.'),
                            html.Div(className='div-for-dropdown',
                                children=[
                                # User input for currency pair
                                    dcc.Dropdown(
                                        id='pairselector', 
                                        options=get_currency_options(fx_df['pair'].unique()), 
                                        multi=True,
                                        value=[fx_df['pair'].sort_values()[0]],
                                        placeholder='Select currency pair...',
                                        style={'backgroundColor': '#1E1E1E'},
                                        className='pairselector'
                                    ),
                                ],
                                style={'color': 'white','margin-bottom': 100}),
                        ]
                    ),
                    # Right Column
                    html.Div(
                        className='eight columns div-for-charts bg-grey',
                        children=[
                            dcc.Graph(
                                id='timeseries', 
                                config={'displayModeBar': False,'showAxisDragHandles':True}, 
                                animate=True),
                            dcc.Graph(
                                id='interestseries', 
                                config={'displayModeBar': False}, 
                                style={'margin-bottom': 100},
                                animate=True),
                            ]
                    )
                ]),

# Map Tab Contents
@app.callback(Output('tab2', 'children'),
              [Input('tabs', 'value')])
def update_tabs(value):
    """ Establish Layout for Map Tab """
    if value == 'Tab2':
        return html.Div([
            html.H2('Currency Flow Map'),
            html.P('Choose a country from the dropdown below to see how its currency performed compared to other currencies over the past month!'),
            html.P('How it works: When you choose a country (key), the map displays how the value of another country\'s currency changed in comparison to the chosen one within the last month. If the other country\'s currency gained value in comparison to the key currency, then the country is highlighted in green. If the other country\'s currency lost value in comparison , then the country is highlighted in red.'),
            html.Div([
                dcc.Dropdown(
                    id="slct_country",
                    options=get_country_options(cc_df['country'].unique()),
                    multi=False,
                    value='USA',
                    style={'width': "40%"}
                    ),
                dcc.Graph(id='fx_map',figure={})
            ]),
            ])

# Populate Currency Flow Map
@app.callback(Output(component_id='fx_map', component_property='figure'),
[Input(component_id='slct_country', component_property='value')])
def update_output(val_selected):
    """ 
    Update map with user selected country and corresponding 
    price action values
    """
    df = map_values(val_selected)
    #print(df)
    fig = px.choropleth(
        df, locations='code',
        color='state',
        hover_name='country',
        hover_data = ir_df[(ir_df['location'] == val_selected) & (ir_df['date'] == date_range[-40])]['value'],
        projection='natural earth')
    fig.update_layout(title=dict(font=dict(size=28),x=0.5,xanchor='center'),
                          margin=dict(l=60, r=60, t=50, b=50))
    return fig

# Populate forex price action chart
@app.callback(
    Output('timeseries', 'figure'),
    [Input('pairselector', 'value')])
def update_graph(pair):
    """ Plot average bid and ask values for selected currency pair """
    trace1 = []
    trace2 = []
    for p in pair:
        trace2.append(
            go.Scatter(
                x=fx_df[fx_df['pair'] == p].index,
                y=fx_df[fx_df['pair'] == p]['avg_ask'],
                mode='lines',
                opacity=0.7,
                name=p + ' Ask',
                textposition='bottom center'))
        trace1.append(
            go.Scatter(
                x=fx_df[fx_df['pair'] == p].index,
                y=fx_df[fx_df['pair'] == p]['avg_bid'],
                mode='lines',
                opacity=0.7,
                name=p + ' Bid',
                textposition='bottom center'))
        traces = [trace1,trace2]
        data = [val for sublist in traces for val in sublist]
        figure = {'data': data,
        'layout': go.Layout(
            colorway=['#5E0DAC', '#FF4F00', '#375CB1', '#FF7400', '#FFF400', '#FF0056'],
            template='plotly_white',
            paper_bgcolor='rgba(0, 0, 0, 0)',
            plot_bgcolor='rgba(0, 0, 0, 0)',
            margin={'b': 15},
            hovermode='x',
            autosize=True,
            xaxis_rangeslider_visible=True,
            title={'text': 'Daily Price Action', 'font': {'color': 'black'}, 'x': 0.5},
            xaxis_title='Date',
            xaxis={
                'showticklabels': True,
                'range': [fx_df.index.min(), fx_df.index.max()],
                'rangeselector': {
                    'buttons': [
                        {
                        'count': 6,
                        'label': '6M',
                        'step': 'month',
                        'stepmode': 'backward',
                        },
                        {
                        'count': 1,
                        'label': '1Y',
                        'step': 'year',
                        'stepmode': 'backward',
                        },
                        {
                        'count': 3,
                        'label': '3Y',
                        'step': 'year',
                        'stepmode': 'backward',
                        },
                        {
                        'count': 5,
                        'label': '5Y',
                        'step': 'year',
                        },
                        {
                        'count': 10,
                        'label': '10Y',
                        'step': 'year',
                        'stepmode': 'backward',
                        },
                        {
                        'label': 'All',
                        'step': 'all',
                        },
                    ]
                },
            },
            ),
        }
    return figure

# Populate Interest Rate Chart
@app.callback(
    Output('interestseries', 'figure'),
    [Input('pairselector', 'value')])
def update_graph(pair):
    """ Plot the 2 interest rates for the selected currency pair """
    trace1 = []
    trace2 = []
    for p in pair:
        base,quote = country_from_pair(p)
        trace1.append(
            go.Scatter(
                x=ir_df[ir_df['location'] == base].index,
                y=ir_df[ir_df['location'] == base]['value'],
                mode='lines',
                opacity=0.7,
                name=base,
                textposition='bottom center'))
        trace2.append(
            go.Scatter(
                x=ir_df[ir_df['location'] == quote].index,
                y=ir_df[ir_df['location'] == quote]['value'],
                mode='lines',
                opacity=0.7,
                name=quote,
                textposition='bottom center'))
        traces = [trace1,trace2]
        data = [val for sublist in traces for val in sublist]
        figure = {
            'data': data,
            'layout': go.Layout(
                colorway=['#5E0DAC', '#FF4F00', '#375CB1', '#FF7400', '#FFF400', '#FF0056'],
                template='plotly_white',
                paper_bgcolor='white', # need to change this to white?
                plot_bgcolor='rgba(0, 0, 0, 0)',
                margin={'b': 15},
                hovermode='x',
                autosize=True,
                xaxis_rangeslider_visible=True,
                title={'text': 'Interest Rate Comparison', 'font': {'color': 'black'}, 'x': 0.5},
                xaxis={
                    'showticklabels': True,
                    'range': [ir_df.index.min(), ir_df.index.max()],
                    'rangeselector': {
                    'buttons': [
                        {
                        'count': 6,
                        'label': '6M',
                        'step': 'month',
                        'stepmode': 'backward',
                        },
                        {
                        'count': 1,
                        'label': '1Y',
                        'step': 'year',
                        'stepmode': 'backward',
                        },
                        {
                        'count': 3,
                        'label': '3Y',
                        'step': 'year',
                        'stepmode': 'backward',
                        },
                        {
                        'count': 5,
                        'label': '5Y',
                        'step': 'year',
                        },
                        {
                        'count': 10,
                        'label': '10Y',
                        'step': 'year',
                        'stepmode': 'backward',
                        },
                        {
                        'label': 'All',
                        'step': 'all',
                        },
                    ]
                },
                },
                xaxis_title='Date',
                yaxis={'showticklabels': True,'range': [ir_df.index.min(), ir_df.index.max()]},
                yaxis_title='Interest Rate (%)',
                ),
        }
#        print('--- Runtime took %s seconds ---' % (time.time() - start_time))
    return figure

if __name__ == '__main__':
    app.run_server(debug=True, port=8051, host='ec2-3-101-124-56.us-west-1.compute.amazonaws.com')
    