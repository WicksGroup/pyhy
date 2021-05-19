'''
Connor Krill - August 2019
Plotly Dashboard Application for viewing the output of hyades simulations
Uses the open source Plotly package to present interactive plots of hyades data
served in a web page viewed from a web browser
'''


import dash
import dash_daq as daq
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
import numpy as np
import pandas as pd
import plotly.graph_objs as go
import os
from hyades_output_reader import createOutput
import json
import re

# Initialize app with style from external_stylesheets
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

'''
Set the layout of the dashboard
'''
app.layout = html.Div([
    # Put title on the top of the page
    html.H1(children=f'Hyades Data Viewer',
           style={'textAlign': 'center'},
           ),
    # Unnessecary subtitle
#    html.H3(children='A convincing argument to ditch matlab',
#           style={'textAlign': 'center'},
#           ),
    # Select file button
    html.Div([
        html.Label('Upload Data'),
        dcc.Upload(
            id='upload-data',
            children=html.Div([
                'Drag and Drop or ',
                html.A('Select Files')
            ]),
            style={
                'width': '90%',
                'height': '60px',
                'lineHeight': '60px',
                'borderWidth': '1px',
                'borderStyle': 'dashed',
                'borderRadius': '5px',
                'textAlign': 'center',
                'margin': 25
            },
            # Allow multiple files to be uploaded
            multiple=True
        ),
    ], style={'width': '49%', 'display': 'inline-block', 'vertical-align':'top',  'justify-content': 'center', 'text-align':'center'}
    ),
    # Button to select the variable to be plotted
    html.Div([
        html.Label('Select Y-Axis Variable'),
        dcc.RadioItems(
            id='yaxis-variable',
            options=[
                {'label':'Pressure', 'value':'Pres'},
                {'label':'Temperature', 'value':'Te'},
                {'label':'Particle Velocity', 'value':'U'},
                {'label':'Density', 'value':'Rho'},
            ],
            value='Pres'
        ),
    ], style={'width': '49%', 'display': 'inline-block',}
    ),
    # Format the graph with the slider
    # No properties of the graph are declared here, just the slider properties
    # All the graph properties are declared out of the update_slider function
    dcc.Graph(id='graph-with-slider'),
    html.Div([
        daq.Slider(
            id='time-slider',
            min=0,
            max=50, # int(hyades.time.max()),
            value=0,
            handleLabel={"showCurrentValue": True,"label": "Time", 'color':'black'},
            marks={int(i):f'{i} ns' for i in np.arange(0, 51, step=5)}, #int(hyades.time.max()) as the uppper limit
            step=0.2,
            updatemode='drag',  
            size=800
        ),
    ], style={'marginBottom': 100, 'marginTop': 25, 'marginLeft': 200, 'marginRight': 200}
    ),
    # Declare the 3D surface / heatmap graph
    # Again no graph properties are specified, they all come out of the update_surface function
    dcc.Graph(id="heatmap-plot"),
    dcc.Graph(id='surface-plot'),
    
    # placeholder variable that is not displayed, just initialized for the intermediate function variables
    html.Div(id='intermediate-value', style={'display': 'none'}) 
])

style_buttons=[
    go.layout.Updatemenu(
                         buttons=list([
                                       dict(label="Viridis",
                                            method="restyle",
                                            args=["colorscale", "Viridis"],
                                            ),
                                       dict(method="restyle",
                                            label="Cividis",
                                            args=["colorscale", "Cividis"]
                                            ),
                                       dict(label="Hot",
                                            method="restyle",
                                            args=["colorscale", "Hot"],
                                            ),
                                       dict(label="Spring",
                                            method="restyle",
                                            args=["colorscale", "Spring"],
                                            ),
                                       ]),
                         type="buttons",
                         direction="right",
                         pad={"r": 10, "t": 10},
                         showactive=True,
                         x=0.5,
                         xanchor="left",
                         y=1.08,
                         yanchor="top",
                         font={"size":12}
                         ),
    go.layout.Updatemenu(
                         buttons=list([
                                       dict(
                                            args=["reversescale", False],
                                            label="False",
                                            method="restyle"
                                            ),
                                       dict(
                                            args=["reversescale", True],
                                            label="True",
                                            method="restyle"
                                            )
                                       ]),
                         type="buttons",
                         direction="right",
                         pad={"r": 10, "t": 10},
                         showactive=True,
                         x=0.8,
                         xanchor="left",
                         y=1.08,
                         yanchor="top",
                         font={"size":12}
                         ),
    ]


@app.callback(Output('intermediate-value', 'children'),
              [Input('yaxis-variable', 'value'),
               Input('upload-data', 'contents')],
              [State('upload-data', 'filename'),
               State('upload-data', 'last_modified')])
def update_output(var, list_of_contents, list_of_names, list_of_dates):
    '''Function loads a hyadesOutput from the selected filename and selected variable
        Output is a json serializable dictionary that can be passed to the plotting functions'''
    if list_of_contents is not None:
        path = "../data"
        filename = list_of_names[0]
        basename = '_'.join( filename.split('_')[0:-1] )
        print('Selected', basename, var)
        # if the basename ends with 3 digits its an optimizer run, so we need a different path
        m = re.search(r'\d{3}$', basename)
        # m is none if there is no match
        if m is not None:
            parent_dir = "_".join( basename.split("_")[:-1] )
            hyades_path = os.path.join(path, parent_dir, basename, basename)
        else:
            hyades_path = os.path.join(path, basename, basename)
        try:
            hyades = createOutput(hyades_path, var)
            data = {'X': hyades.X.tolist(),
                    'time': hyades.time.tolist(),
                    'output': hyades.output.tolist(),
                    'var': var,
                    'material properties': hyades.material_properties,
                    'filename':basename
                   }
        except Exception as e:
            print(e)
            print(hyades_path)
            data = {'X': [1,2,3],
                    'time': [4,5,6],
                    'output': [[0,0,0],[0,1,0],[0,0,0]],
                    'var': 'Uh-Oh',
                    'material properties': 'OOPS',
                    'filename': 'Something went wrong'
                   }              
        
        return json.dumps(data)



# decorator specifices which variables to take as inputs
# the "Input" is called everytime the value changes
# this function updates the surface
@app.callback(
    Output('surface-plot', 'figure'),
    [Input('intermediate-value', 'children')])
def update_surface(children):
    '''Function to update the 3D surface plot of the variable history
        Includes buttons to change to heat map and simple controls for the colormap'''
    if children is None:
        return {
        'data': [go.Surface(x=[1,2,3], y=[4,5,6], z=[[0,0,0,],[0,1,0],[0,0,0]],
                         colorscale='Viridis',
                       )
            ],
        'layout': go.Layout(title=f'Children is None Error',
                             autosize=True, height=800,
                             scene={"xaxis": {'title': ""},
                                    "yaxis": {"title": ""},
                                    "zaxis": {"title": ""},
                                    'aspectratio': dict(x=1, y=1, z=0.7),
                                    'aspectmode': "manual"
                                   },
                             template="plotly_white",
                             xaxis={'title': ''},
                             yaxis={'title': ''}, 
                  )
    }

    # load the intermediate variables into useful numpy arrays
    data = json.loads(children)
    X      = np.array(data['X'])
    time   = np.array(data['time'])
    output = np.array(data['output'])
    var = data['var']
    material_properties = data['material properties']

    if var=='Te':     label, units = 'Temperature', '(K)'
    elif var=='Pres': label, units = 'Pressure', '(GPa)'
    elif var=='U':    label, units = 'Particle Velocity', '(km/s)'
    elif var=='Rho':  label, units = 'Density', '(g/cc)'
    else: label, units = 'Unknown', 'Variable'
    #    df = pd.DataFrame(data) # trying to get the labels on the surface plot to say their variable names
    traces = [go.Surface(x=data['time'], y=data['X'], z=data['output'],
                         colorscale='Viridis',
                         colorbar={"title": f'{label} {units}', "len": 0.75,
                         'title_font':{'size':24}, 'tickfont':{'size':18}, "titleside":"right"}
                       )
            ]
#    annotations = []
    for mat in material_properties:
        mat_X = mat['startX']
        index = np.argmin( abs(X - mat_X) )
        
        x = 5
        y = (mat['startX'] + mat['endX']) / 2
        z = output.max() * 0.8
        
#        annotations.append(dict(x=y,
#                                y=x,
#                                z=z,
#                                text=mat,
#                                showarrow=False,
#                                ax=0,
#                                ay=-50,
#                                font=dict(
#                                          color="black",
#                                          size=12)))

        traces.append(
               go.Scatter3d(x=time, y=[mat_X]*len(time), z=output[index,:],
                            name=mat['material'],
                            mode='lines',
                            line=dict(color='black', width=6, dash='dash'),
                            visible=False,
                            )
        )

    layer_buttons =  [go.layout.Updatemenu(
                         buttons=list([
                                       dict(label="Hide Layer Interface",
                                            method="update",
                                            args=[{"visible": [True, False, False, False]},
#                                                  {"title": "Hide annotations",
#                                                  "annotations":[]}
                                                  ]),
                                       dict(label="Show Layer Interface",
                                            method="update",
                                            args=[{"visible": [True]*4},
#                                                  {"title": "Show annotations",
#                                                  "annotations":annotations}
                                                  ])]),
                         type="buttons",
                         direction="right",
                         pad={"r": 10, "t": 10},
                         showactive=True,
                         x=0.1,
                         xanchor="left",
                         y=1.08,
                         yanchor="top",
                         font={"size":12}
                         ),
                      ]


    
    return {
        'data': traces,
        'layout': go.Layout(title=f'{data["filename"]} {label} Profile',
                            font=dict( size=16 ), #,family='Courier New, monospace', color='#7f7f7f')
                            autosize=True, height=800,
                            scene={"xaxis": {'title': "Nanoseconds"},
                                   "yaxis": {"title": "Lagranian Distance"},
                                   "zaxis": {"title": label},
                                   'aspectratio': dict(x=1, y=1, z=0.7),
                                   'aspectmode': "manual",
                                   },
                            template="plotly_white",
                            xaxis={'title': 'Nanoseconds'},
                            yaxis={'title': 'Lagranian Distance'},
                            updatemenus=layer_buttons + style_buttons,
                            
                  )
    }


######################################################
@app.callback(
              Output('heatmap-plot', 'figure'),
              [Input('intermediate-value', 'children')])
def update_heatmap(children):
    '''Function to update the 3D heatmap plot of the variable history
        Includes buttons to change to heat map and simple controls for the colormap'''
    if children is None:
        return {
        'data': [go.Heatmap(x=[1,2,3], y=[4,5,6], z=[[0,0,0,],[0,1,0],[0,0,0]],
                            )
                 ],
                 'layout': go.Layout(title=f'Children is None Error',
                                     autosize=True, height=800,
                                     scene={"xaxis": {'title': ""},
                                     "yaxis": {"title": ""},
                                     },
                                     template="plotly_white",
                                     xaxis={'title': '',},
                                     yaxis={'title': ''},
#                                     title_font=dict(size=18),
#                                     tickfont  =dict(size=18)
                                     )
    }

    # load the intermediate variables into useful numpy arrays
    data = json.loads(children)
    X      = np.array(data['X'])
    time   = np.array(data['time'])
    output = np.array(data['output'])
    var = data['var']
    material_properties = data['material properties']

    if var=='Te':     label, units = 'Temperature', '(K)'
    elif var=='Pres': label, units = 'Pressure', '(GPa)'
    elif var=='U':    label, units = 'Particle Velocity', '(km/s)'
    elif var=='Rho':  label, units = 'Density', '(g/cc)'
    else: label, units = 'Unknown', 'Variable'
        
    traces = [go.Heatmap(x=time, y=X, z=output,
                         type = 'heatmap',
                         colorscale = 'Viridis',
                         colorbar={"title": f'{label} {units}', "len": 0.75,
                         'title_font':{'size':24}, 'tickfont':{'size':18}, "titleside":"right"})]
    annotations = []
    for mat in material_properties:
        mat_X = mat['startX']
        index = np.argmin( abs(X - mat_X) )
        x = (0, time.max())
        y = [mat_X] * 2
        traces.append(
                      go.Scatter(x=x, y=y,
                                 name=mat['material'],
                                 mode='lines',
                                 line=dict(color='white', width=2, dash='dash'),
                                 visible=False,
                                 showlegend=False,
                                 )
                      )

        x = 100,
        y = (mat['startX'] + mat['endX']) / 2
        annotations.append(dict(x=x,
                                y=y,
                                text=mat,
                                showarrow=False,
                                ax=0,
                                ay=-50,
                                font=dict(color="white",
                                          size=16),
                                 align="left")
                           )
    layer_buttons =  [go.layout.Updatemenu(
                                           buttons=list([
                                                         dict(label="Hide Layer Interface",
                                                              method="update",
                                                              args=[{"visible": [True, False, False, False]},
                                                                    {"annotations":[]}
                                                                    ]),
                                                         dict(label="Show Layer Interface",
                                                              method="update",
                                                              args=[{"visible": [True]*4},
                                                                    {"annotations":annotations}
                                                                    ])]),
                                           type="buttons",
                                           direction="right",
                                           pad={"r": 10, "t": 10},
                                           showactive=True,
                                           x=0.1,
                                           xanchor="left",
                                           y=1.08,
                                           yanchor="top",
                                           font={'size':12}
                                           ),
                      ]
    return {
        'data': traces,
            'layout': go.Layout(title=f'{data["filename"]} {label} Profile',
                                font=dict( size=24 ),
                                autosize=True, height=800,
                                scene={"xaxis": {'title': "Nanoseconds"},
                                       "yaxis": {"title": "Lagranian Distance"},
                                },
                                template="plotly_white",
                                xaxis={'title': 'Nanoseconds',},# 'title_font':{'size':24}, 'tickfont':{'size':24}},
                                yaxis={'title': 'Lagranian Distance',},# 'title_font':{'size':24}, 'tickfont':{'size':24}},
                                updatemenus=layer_buttons + style_buttons
                                )
    }
######################################################

file  = './DatasaurusDozen.csv'
df = pd.read_csv(file)
#df = df.loc[df.dataset=='dino']
#print(df.columns)
dino_x = [x+50 for x in list(df.x)]
dino_y = list(df.y)

@app.callback(
    Output('graph-with-slider', 'figure'),
    [Input('time-slider', 'value'),
     Input('intermediate-value', 'children')])
def update_lineout(selected_time, children):
    '''Update the slider when a new time is selected or the file is changed'''
    if children is None:
        return {
        'data': [go.Scatter(x=dino_x, y=dino_y, #x=np.linspace(0,100,1000), y=25*np.sin(np.linspace(0,100,1000)),
                            mode='markers',
                            line=dict(width=4))],
        'layout': go.Layout(
            xaxis={'title': 'Amount this plot looks like a dinosaur', 'range':(0, 200)},
            yaxis={'title': 'Likelihood a dinosaur wrote this code', 'range':(0, 100)},
            margin={'l': 200, 'b': 40, 't': 75, 'r': 200},
            hovermode='closest'
        )
    }    
    
    data = json.loads(children)
    X      = np.array(data['X'])
    time   = np.array(data['time'])
    output = np.array(data['output'])
    var = data['var']
    material_properties = data['material properties']

    if var=='Te':     label, units = 'Temperature', '(K)'
    elif var=='Pres': label, units = 'Pressure', '(GPa)'
    elif var=='U':    label, units = 'Particle Velocity', '(km/s)'
    elif var=='Rho':  label, units = 'Density', '(g/cc)'
    index = np.argmin(abs(time - selected_time))
    traces = []
    annotations = []
    for mat in material_properties:
        start = mat['startMesh'] - 1
        if start < 0: # check for the first material condition
            start = 0
        stop = mat['endMesh']
        if stop > len(X) - 1:
            stop = len(X) - 1

        traces.append(
            go.Scatter(x=X[start:stop], y=output[start:stop, index],
                       name=mat['material'],
                       line=dict(width=4),
                      )
        )
        dashedX = [mat['endX']] * 2
        dashedY = [0, output.max() + 1]
        traces.append(
            go.Scatter(x=dashedX, y=dashedY,
                       showlegend=False,
                       line=dict(color='black', width=1, dash='dot')
                      )
        )
        annotations.append(go.layout.Annotation(
                    x=(mat['startX'] + mat['endX']) / 2,
                    y=output.max() * 0.9,
#                     xref="x",
#                     yref="y",
                    text=mat['material'],
                    font=dict(color="black",
                              size=16),
                    showarrow=False))
        
    return {
        'data': traces,
        'layout': go.Layout(
            title=f'{data["filename"]} {label} Profile',
            font=dict( size=18 ),
            xaxis={'title': 'Lagranian Distance',},# 'title_font':{'size':24}, 'tickfont':{'size':16} },
            yaxis={'title': f'{label} {units}',},#   'title_font':{'size':24}, 'tickfont':{'size':16}, 'range':(0, output.max())},
            margin={'l': 200, 'b': 40, 't': 75, 'r': 200},
            hovermode='closest',
            annotations=annotations,
        )
    }


if __name__ == '__main__':
    PORT = '8000'
    ADDRESS = '127.0.0.1'
    app.run_server(port=PORT, debug=True) #  host=ADDRESS,
