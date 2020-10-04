

import dash
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
import plotly.express as px
import psycopg2
import plotly.graph_objs as go

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

# ------------------------------------------------------------------------------
# Import and clean data (importing csv into pandas)
df_gdp = pd.read_csv('https://stats.oecd.org/sdmx-json/data/DP_LIVE/.QGDP.TOT.PC_CHGPP.Q/OECD?contentType=csv&detail=code&separator=comma&csv-lang=en&startPeriod=2018-Q4&endPeriod=2020-Q2', usecols = ['LOCATION','TIME','Value'])
print(df)
df_ir = pd.read_csv('https://stats.oecd.org/sdmx-json/data/DP_LIVE/.STINT.TOT.PC_PA.M/OECD?contentType=csv&detail=code&separator=comma&csv-lang=en&startPeriod=1956-01&endPeriod=2020-09', usecols = ['LOCATION', 'TIME', 'Value'])

# Connect to postgreSQL database
pgconnect = psycopg2.connect(\
    host = '***', \
    port = 5431,
    database = '***',
    user = '***',
    password = "***")
pgcursor = pgconnect.cursor()

# Download forecast data table
pgcursor.execute("SELECT * FROM fx_data")
fx_df = pd.DataFrame(pgcursor.fetchall(),
    columns=['pair', 'date', 'min_bid', 'max_bid', 'avg_bid', 
             'min_ask', 'max_ask', 'avg_ask'])
# ------------------------------------------------------------------------------

# need to split into base and 
unique_pairs = fx_df['pair'].unique()
pairs = [('GBP','USD'),('USD','JPY')]
print(pairs)

GBP_pair = fx_df.iloc[:,1:3]
print(GBP_pair)

# fig = px.line(GBP_pair, x="date", y="min_bid", title='Life expectancy in Canada')
# fig.show()

fig = go.Figure(data=[go.Scatter(x=[1, 2, 3], y=[4, 1, 2])])
dcc.Graph(
        id='example-graph-2',
        figure=fig
    )
fig.show()

app.layout = html.Div([
    # html.Div([
    #     dcc.Graph(id='gbpusd')
    # ],className='nine columns'),

    dcc.Dropdown(
        id='demo-dropdown',
        options=[
            {'label': 'Daily Min', 'value': 'Daily Min'},
            {'label': 'USDJPY', 'value': 'USDJPY'},
            {'label': 'EURUSD', 'value': 'EURUSD'}
        ],
        value='GBPUSD'
    ),
    html.Div(id='dd-output-container')
])





if __name__ == '__main__':
    app.run_server(debug=True, port=8050, host="ec2-3-101-124-56.us-west-1.compute.amazonaws.com")