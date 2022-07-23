import pandas as pd
import dash
import plotly.graph_objects as go
import plotly.express as px
import dash_bootstrap_components as dbc
from dash import  html, dcc, Input, Output

### importing and preprocessing data
df = pd.read_csv('data/games.csv')
df['Date']=pd.to_datetime(df['Date'],format='%m/%d/%Y')
df.drop(['game_id','opponent_rating','analysis'],axis=1,inplace=True)

df.opening=df.opening.str.split(':').str[0]
df.winner=df.winner.fillna('draw')
openings=list(df.opening.unique())
df['wining']=df.winner
for i in range(len(df)):
    if df.at[i,'winner']=='draw':
        continue
    elif df.at[i,'winner']==df.at[i,'color']:
        df.at[i,'wining']='won'
    else:
        df.at[i,'wining']='lost'
### helping functions
def filter_inputs(data,speed,color,opening):
    if speed=='all' and color=='all':
        pass
    if speed=='all' and color!='all':
        data=data[data.color==color]
    if speed!='all' and color=='all':
        data= data[data.speed==speed]
    if speed!='all' and color!='all':
        data= data.loc[(data.speed==speed)&(data.color==color)]
    if opening=='all':
        return data
    
    data=data[data.opening == opening]
    return data

def get_pie(data,col):
    data=data.groupby([col]).size().reset_index()
    data.columns=[col,'count']
    return data
def month(row):
    date=str(row)
    look_up = {'1': 'Jan', '2': 'Feb', '3': 'Mar', '4': 'Apr', '5': 'May',
            '6': 'Jun', '7': 'Jul', '8': 'Aug', '9': 'Sep', '10': 'Oct', '11': 'Nov', '12': 'Dec'}
    return look_up[date]
def get_data_rating(data,Range):
    data = data.groupby(['Date','speed'])[['rating']].mean()
    data.reset_index(inplace=True)
    dates = [tsp.value for tsp in data['Date']]
    first_date = pd.to_datetime(round(min(dates) + (Range[0]/24)*(max(dates)-min(dates))))
    last_date = pd.to_datetime(round(min(dates) + (Range[1]/24)*(max(dates)-min(dates))))
    data = data[(data['Date']>=first_date)&(data['Date']<=last_date)]
    print(data)
    return data
def get_data_accuracy(data,col):
    
    
    data['month']=data['Date'].dt.month
    data=data.groupby(['month'])[[col]].mean().reset_index()
    data['month'] = data['month'].apply(month)
    return data
def get_data_(data,cols):
    
    
    data['month']=data['Date'].dt.month
    data=data.groupby(['month'])[[col for col in cols]].mean().reset_index()
    data['month'] = data['month'].apply(month)
    return data
def opening(data):
    data.opening=data.opening.str.split(':').str[0]

    data=data.groupby(['opening'])['wining'].agg(['count']).sort_values('count',ascending=False)[:12]
    data.reset_index(inplace=True)  
    
    fig = px.bar(
            data,
            x='count',
            y='opening',
            template='plotly_dark',
            orientation='h',
        )
    fig.update_layout(
            font_family="Courier New",
            title_font_family="Times New Roman",
        )
    """
    fig = go.Figure(go.Bar(
            x=data['count'],
            y=data['opening'],
            

            marker=dict(
                color='rgba(50, 171, 96, 0.6)',
                line=dict(
                    color='rgba(50, 171, 96, 1.0)',
                    width=1),

            ),
            orientation='h',
        ))
    """
    return fig  
### dash application

app=dash.Dash('app1',external_stylesheets=[dbc.themes.DARKLY])

### app layout

app.layout=dbc.Container([

    html.H1('Chess Analysis',className='pt-5',style={'textAlign': 'center','color':''}),
    dbc.Row([
        
        dbc.Col([
            html.H3('Ratings',className='pt-5',style={'textAlign': 'center','color':''}),
            html.Div([
                dcc.Graph(figure={},id='graph6'),
                dcc.RangeSlider(1, 12, marks=None, value=[3, 11], id='my-range-slider')
            ],style={'width':'100%','height':'auto'}),
            ]),
        dbc.Col([
            html.H3('Repertoire',className='pt-5',style={'textAlign': 'center','color':''}),
            html.Div([
                dcc.Graph(figure=opening(df)),
            ],style={'width':'100%','height':'auto'}),])
            ]),

    html.Div([
        
        html.Div([
            html.H4('Pace', style={'textAlign': 'center'}),
            dcc.Dropdown(
                id='speed',
                placeholder='Blitz or Rapid',
                options=[{'label':'all','value':'all'},
                {'label':'blitz','value':'blitz'},
                {'label':'rapid','value':'rapid'},
                {'label':'bullet','value':'bullet'}],
                value='blitz',style={'width':'200px','padding-left':'15px','color': 'green'})
            ],style={'display':'flex','flex-direction':'column','align-items': 'center','justify-content':'space-between','width':'33%'}),
        html.Div([
            html.H4('Color', style={'textAlign': 'center'}),
            dcc.Dropdown(
                id='color',
                options=[{'label':'all','value':'all'},
                {'label':'white','value':'white'},
                {'label':'black','value':'black'}],
                value='black',style={'width':'200px','padding-left':'15px','color': 'green'})
            ],style={'display':'flex','flex-direction':'column','align-items': 'center','justify-content':'space-between','width':'33%'}),
        html.Div([
            html.H4('Opening', style={'textAlign': 'center'}),
            dcc.Dropdown(
                id='opening',
                options=[{'label':'all','value':'all'}]+[{'label':i,'value':i} for i in openings],
                value='Lion Defense',
                style={'width':'200px','padding-left':'15px','color': 'green'}
                )
            ],style={'display':'flex','flex-direction':'column','align-items': 'center','justify-content':'space-between','width':'33%'}),
    ],className='py-5 d-flex'),
    html.Br(),
    html.Br(),
    html.Div(id='games'),
    html.H3('Stats',className='py-4', style={'textAlign': 'center'}),
    dbc.Row([
        
        dbc.Col([
            html.H3('Win Rate', style={'textAlign': 'center'}),
            dcc.Graph(figure={},id='graph0')
            ]),
        dbc.Col([
            html.H3('Ending', style={'textAlign': 'center'}),
            dcc.Graph(figure={},id='graph1')
        
    ])]
    ),
    html.Br(),
    dbc.Row([
        
        dbc.Col([
            html.H3('Accuracies', style={'textAlign': 'center'}),
            dcc.Graph(figure={},id='graph2')
            ]),
        dbc.Col([
            html.H3('Inaccuracies-Mistakes-Blunders', style={'textAlign': 'center'}),
            dcc.Graph(figure={},id='graph3')
        
    ])]
    ),
    ]
    )

### app interactivity
@app.callback(
            Output(component_id='graph6',component_property='figure'),
            [Input(component_id='my-range-slider',component_property='value'),
            ])
def get_graphs(Range):

    data = get_data_rating(df,Range)
    
    
    
    fig= px.line(data, x="Date", y="rating", color='speed',template='plotly_dark')
        
    
    return fig
@app.callback(Output(component_id='games',component_property='children'),
               [Input(component_id='speed',component_property='value'),
               Input(component_id='color',component_property='value'),
               Input(component_id='opening',component_property='value')])
def get_graphs(speed,color,opening):
    
    
    Data=filter_inputs(df,speed,color,opening)
    
    return [html.H3('Total Games:' + str(len(Data)) + ' games',className='mb-5 text-center text-primary')]

@app.callback(
            Output(component_id='graph0',component_property='figure'),
            [Input(component_id='speed',component_property='value'),
            Input(component_id='color',component_property='value'),
            Input(component_id='opening',component_property='value')])
def get_graphs(speed,color,opening):


    Data=filter_inputs(df,speed,color,opening)


    fig0=px.pie(get_pie(Data,'wining'),template='plotly_dark',hole=.7, values='count', names='wining', title='wining pie chart')
    
    return fig0

@app.callback(
            Output(component_id='graph1',component_property='figure'),
            [Input(component_id='speed',component_property='value'),
            Input(component_id='color',component_property='value'),
            Input(component_id='opening',component_property='value')])
def get_graphs(speed,color,opening):
    
    
    Data=filter_inputs(df,speed,color,opening)
    
    
    
    fig1=px.pie(get_pie(Data,'game_ending'),template='plotly_dark',hole=.7, values='count', names='game_ending', title='game_ending pie chart')
    
    return fig1

@app.callback(
            Output(component_id='graph2',component_property='figure'),
            [Input(component_id='speed',component_property='value'),
            Input(component_id='color',component_property='value'),
            Input(component_id='opening',component_property='value')])
def get_graphs(speed,color,opening):
    
    
    Data=filter_inputs(df,speed,color,opening)
    
    
    
    fig2=px.bar(get_data_accuracy(Data,'accuracy'),template='plotly_dark',y='accuracy',x='month')
    
    return fig2

@app.callback(
            Output(component_id='graph3',component_property='figure'),
            [Input(component_id='speed',component_property='value'),
            Input(component_id='color',component_property='value'),
            Input(component_id='opening',component_property='value')])
def get_graphs(speed,color,opening):
    
    
    Data=filter_inputs(df,speed,color,opening)
    
    
    fig3=px.bar(get_data_(Data,['inaccuracy','mistake','blunder']),template='plotly_dark',y=['inaccuracy','mistake','blunder'],x='month')
    return fig3
"""
@app.callback(
            Output(component_id='graph4',component_property='figure'),
            [Input(component_id='speed',component_property='value'),
            Input(component_id='color',component_property='value'),
            Input(component_id='opening',component_property='value')])
def get_graphs(speed,color,opening):
    
    
    Data=filter_inputs(df,speed,color,opening)
    
    
    fig4=px.bar(get_data(Data,'mistake'),template='none',y='mistake',x='month')
    return fig4

@app.callback(
            Output(component_id='graph5',component_property='figure'),
            [Input(component_id='speed',component_property='value'),
            Input(component_id='color',component_property='value'),
            Input(component_id='opening',component_property='value')])
def get_graphs(speed,color,opening):
    
    
    Data=filter_inputs(df,speed,color,opening)
    
    
    
    fig5=px.bar(get_data(Data,'blunder'),template='none',y='blunder',x='month')
    return fig5
    

"""

if __name__=='__main__':
    app.run_server(debug=True, port=3000)

