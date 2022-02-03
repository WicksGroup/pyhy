"""Plotly Dashboard Application for viewing the output of hyades simulations
Uses the open source Plotly package to present interactive plots of hyades data
served in a web page viewed from a web browser

Todo:
    - Update existing references to material properties to the new HyadesOutput Layer dictionaries

"""
import os
import sys
import re
import json
import dash
from dash.dependencies import Input, Output, State
import dash_daq as daq
from dash import html, dcc
import numpy as np
import pandas as pd
import plotly.graph_objs as go
sys.path.append('../')
from tools.hyades_reader import HyadesOutput


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
    ], style={'width': '49%', 'display': 'inline-block', 'vertical-align': 'top',
              'justify-content': 'center', 'text-align': 'center'}
    ),
    # Button to select the variable to be plotted
    html.Div([
        html.Label('Select Y-Axis Variable'),
        dcc.RadioItems(
            id='yaxis-variable',
            options=[
                {'label': 'Pressure', 'value': 'Pres'},
                {'label': 'Temperature', 'value': 'Te'},
                {'label': 'Particle Velocity', 'value': 'U'},
                {'label': 'Density', 'value': 'Rho'},
            ],
            value='Pres'
        ),
    ], style={'width': '49%', 'display': 'inline-block'}
    ),
    # Format the graph with the slider
    # No properties of the graph are declared here, just the slider properties
    # All the graph properties are declared out of the update_slider function
    dcc.Graph(id='graph-with-slider'),
    html.Div([daq.Slider(id='time-slider',
                         min=0,
                         max=50,  # int(hyades.time.max()),
                         value=0,
                         handleLabel={"showCurrentValue": True, "label": "Time", 'color': 'black'},
                         marks={int(i): f'{i} ns' for i in np.arange(0, 51, step=5)},  # int(hyades.time.max()) as the upper limit
                         step=0.2,
                         updatemode='drag',
                         size=800
                         )],
             style={'marginBottom': 100, 'marginTop': 25, 'marginLeft': 200, 'marginRight': 200}
             ),
    # Declare the 3D surface / heatmap graph
    # Again no graph properties are specified, they all come out of the update_surface function
    html.Div(
        dcc.Graph(id="heatmap-plot"),
        style={'marginBottom': 100,
               'marginTop': 25,
               'marginLeft': 200,
               'marginRight': 200,
               'display': 'inline-block',
               "transform": "translate(25%, -25%)"
               }
    ),

    dcc.Graph(id='surface-plot'),
    
    # placeholder variable that is not displayed, just initialized for the intermediate function variables
    html.Div(id='intermediate-value', style={'display': 'none'}) 
])

style_buttons = [
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
                         font={"size": 12}
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
                         font={"size": 12}
                         ),
    ]


@app.callback(Output('intermediate-value', 'children'),
              [Input('yaxis-variable', 'value'),
               Input('upload-data', 'contents')],
              [State('upload-data', 'filename'),
               State('upload-data', 'last_modified')])
def update_output(var, list_of_contents, list_of_names, list_of_dates):
    """Function loads a HyadesOutput from the selected filename and selected variable

    Args:
        var:
        list_of_contents:
        list_of_names:
        list_of_dates:

    Returns:
        json.dump : json serializable dictionary formatted for plotting functions
    """

    if list_of_contents is not None:
        filename = os.path.splitext(list_of_names[0])[0]

        hyades_path = os.path.join('..', 'data', filename)

        if os.path.isdir(hyades_path):  # Check if the selected file is from an optimization
            contains_optimization_json = any([file.endswith('_optimization.json') for file in os.listdir(hyades_path)])
            if contains_optimization_json:
                basename = filename[0:-4]  # Remove underscore and three digits at end of filename
                hyades_path = os.path.join('..', 'data', basename, filename)

        try:
            print(hyades_path)
            hyades = HyadesOutput(hyades_path, var)
            data = {'X': hyades.x[0, :].tolist(),
                    'time': hyades.time.tolist(),
                    'output': hyades.output.tolist(),
                    'var': var,
                    'layers': hyades.layers,
                    'filename': filename
                    }
        except Exception as e:
            print(e)
            print(hyades_path)
            data = {'X': [1, 2, 3],
                    'time': [4, 5, 6],
                    'output': [[0, 0, 0], [0, 1, 0], [0, 0, 0]],
                    'var': 'Uh-Oh',
                    'layers': 'OOPS',
                    'filename': 'Something went wrong'
                    }
        
        return json.dumps(data)


# decorator specifies which variables to take as inputs
# the "Input" is called every time the value changes
@app.callback(
    Output('surface-plot', 'figure'),
    [Input('intermediate-value', 'children')])
def update_surface(children):
    """Function to update the 3D surface plot of the variable history
    Includes buttons to change to heat map and simple controls for the colormap

    Args:
        children:

    Returns:

    """

    if children is None:
        return {
                'data': [go.Surface(x=[1, 2, 3], y=[4, 5, 6], z=[[0, 0, 0], [0, 1, 0], [0, 0, 0]],
                                    colorscale='Viridis')
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
    X = np.array(data['X'])
    time = np.array(data['time'])
    output = np.array(data['output'])
    var = data['var']
    layers = data['layers']
    print('LAYERS', layers)
    for layer in layers:
        print('LAYER:', layer, 'VALUES:', layers[layer])

    if var == 'Te':
        label, units = 'Temperature', '(K)'
    elif var == 'Pres':
        label, units = 'Pressure', '(GPa)'
    elif var == 'U':
        label, units = 'Particle Velocity', '(km/s)'
    elif var == 'Rho':
        label, units = 'Density', '(g/cc)'
    else:
        label, units = 'Unknown', 'Variable'
    #    df = pd.DataFrame(data) # trying to get the labels on the surface plot to say their variable names
    traces = [go.Surface(x=data['time'], y=data['X'], z=data['output'],
                         colorscale='Viridis',
                         colorbar={"title": f'{label} {units}', "len": 0.75,
                         'title_font': {'size': 24}, 'tickfont': {'size': 18}, "titleside": "right"}
                         )
              ]
    # annotations = []
    for layer in layers:
        index = np.argmin(abs(X - layers[layer]['X Start']))
        
        # x = 5
        # y = (layers[layer]['X Start'] + layers[layer]['X Stop']) / 2
        # z = output.max() * 0.8
        # annotations.append(dict(x=y,
        #                         y=x,
        #                         z=z,
        #                         text=layers[layer]['Name'],
        #                         showarrow=False,
        #                         ax=0,
        #                         ay=-50,
        #                         font=dict(
        #                                   color="black",
        #                                   size=12)))

        traces.append(go.Scatter3d(x=time,
                                   y=[layers[layer]['X Start']]*len(time),
                                   z=output[index, :],
                                   name=layers[layer]['Name'],
                                   mode='lines',
                                   line=dict(color='black', width=6, dash='dash'),
                                   visible=False,
                                   )
                      )

    layer_buttons = [go.layout.Updatemenu(
                         buttons=list([
                                       dict(label="Hide Layer Interface",
                                            method="update",
                                            args=[{"visible": [True, False, False, False]},
                                                  # {"title": "Hide annotations",
                                                  # "annotations":[]}
                                                  ]),
                                       dict(label="Show Layer Interface",
                                            method="update",
                                            args=[{"visible": [True]*4},
                                                  # {"title": "Show annotations",
                                                  # "annotations":annotations}
                                                  ])
                                        ]),
                         type="buttons",
                         direction="right",
                         pad={"r": 10, "t": 10},
                         showactive=True,
                         x=0.1,
                         xanchor="left",
                         y=1.08,
                         yanchor="top",
                         font={"size": 12}
                         ),
                     ]
    
    return {
            'data': traces,
            'layout': go.Layout(title=f'{data["filename"]} {label} Profile',
                                font=dict(size=16),  # family='Courier New, monospace', color='#7f7f7f')
                                autosize=True, height=800,
                                scene={"xaxis": {'title': "Nanoseconds"},
                                       "yaxis": {"title": "Lagrangian Distance"},
                                       "zaxis": {"title": label},
                                       'aspectratio': dict(x=1, y=1, z=0.7),
                                       'aspectmode': "manual",
                                       },
                                template="plotly_white",
                                xaxis={'title': 'Nanoseconds'},
                                yaxis={'title': 'Lagrangian Distance'},
                                updatemenus=layer_buttons + style_buttons
                                )
            }


@app.callback(
              Output('heatmap-plot', 'figure'),
              [Input('intermediate-value', 'children')])
def update_heatmap(children):
    """Update the 3D heatmap plot of the variable history.
    Includes buttons to change to heat map and simple controls for the colormap

    Args:
        children:

    Returns:

    """
    if children is None:
        return {
                'data': [go.Heatmap(x=[1, 2, 3], y=[4, 5, 6], z=[[0, 0, 0, ], [0, 1, 0], [0, 0, 0]],
                                    )
                         ],
                'layout': go.Layout(title=f'Children is None Error',
                                    autosize=True, height=800,
                                    scene={"xaxis": {'title': ""},
                                           "yaxis": {"title": ""},
                                           },
                                    template="plotly_white",
                                    xaxis={'title': ''},
                                    yaxis={'title': ''},
                                    # title_font=dict(size=18),
                                    # tickfont=dict(size=18)
                                    )
                }

    # load the intermediate variables into useful numpy arrays
    data = json.loads(children)
    X = np.array(data['X'])
    time = np.array(data['time'])
    output = np.array(data['output'])
    var = data['var']
    layers = data['layers']

    if var == 'Te':
        label, units = 'Temperature', '(K)'
    elif var == 'Pres':
        label, units = 'Pressure', '(GPa)'
    elif var == 'U':
        label, units = 'Particle Velocity', '(km/s)'
    elif var == 'Rho':
        label, units = 'Density', '(g/cc)'
    else:
        label, units = 'Unknown', 'Variable'
        
    traces = [go.Heatmap(x=time, y=X, z=output,
                         type='heatmap',
                         colorscale='Viridis',
                         colorbar={"title": f'{label} {units}', "len": 0.75,
                                   'title_font': {'size': 24}, 'tickfont': {'size': 18}, "titleside": "right"}
                         )
              ]
    annotations = []
    for layer in layers:
        x_start = layers[layer]['X Start']
        index = np.argmin(abs(X - x_start))
        x = (0, time.max())
        y = [x_start] * 2
        traces.append(
                      go.Scatter(x=x, y=y,
                                 name=layers[layer]['Name'],
                                 mode='lines',
                                 line=dict(color='white', width=2, dash='dash'),
                                 visible=False,
                                 showlegend=False,
                                 )
                      )
        x = 100,
        y = (layers[layer]['X Start'] + layers[layer]['X Stop']) / 2
        annotations.append(dict(x=x,
                                y=y,
                                text=layers[layer]['Name'],
                                showarrow=False,
                                ax=0,
                                ay=-50,
                                font=dict(color="white",
                                          size=16),
                                align="left")
                           )
    layer_buttons = [go.layout.Updatemenu(
                                          buttons=list([
                                                        dict(label="Hide Layer Interface",
                                                             method="update",
                                                             args=[{"visible": [True, False, False, False]},
                                                                   {"annotations": []}
                                                                   ]),
                                                        dict(label="Show Layer Interface",
                                                             method="update",
                                                             args=[{"visible": [True]*4},
                                                                   {"annotations": annotations}
                                                                   ])
                                                        ]),
                                          type="buttons",
                                          direction="right",
                                          pad={"r": 10, "t": 10},
                                          showactive=True,
                                          x=0.1,
                                          xanchor="left",
                                          y=1.08,
                                          yanchor="top",
                                          font={'size': 12}
                                          ),
                     ]
    return {
            'data': traces,
            'layout': go.Layout(title=f'{data["filename"]} {label} Profile',
                                font=dict(size=24),
                                autosize=True, height=800, width=800*1.61803,
                                scene={"xaxis": {'title': "Nanoseconds"},
                                       "yaxis": {"title": "Lagrangian Distance"},
                                       },
                                template="plotly_white",
                                xaxis={'title': 'Nanoseconds', 'constrain': 'domain'},  # 'title_font':{'size':24}, 'tickfont':{'size':24}},
                                yaxis={'title': 'Lagrangian Distance', 'scaleratio': 1},  # 'title_font':{'size':24}, 'tickfont':{'size':24}},
                                updatemenus=layer_buttons + style_buttons
                                )
            }


@app.callback(
    Output('graph-with-slider', 'figure'),
    [Input('time-slider', 'value'),
     Input('intermediate-value', 'children')])
def update_lineout(selected_time, children):
    """Update the slider when a new time is selected or the file is changed

    Args:
        selected_time:
        children:

    Returns:

    """
    if children is None:  # If there is no file selected, load temporary data
        file = './DatasaurusDozen.csv'
        df = pd.read_csv(file)
        dino_x = [x + 50 for x in list(df.x)]
        dino_y = list(df.y)
        return {'data': [go.Scatter(x=dino_x, y=dino_y,
                                    mode='markers',
                                    line=dict(width=4))],
                'layout': go.Layout(xaxis={'title': 'Amount this plot looks like a dinosaur', 'range': (0, 200)},
                                    yaxis={'title': 'Likelihood a dinosaur wrote this code', 'range': (0, 100)},
                                    margin={'l': 200, 'b': 40, 't': 75, 'r': 200},
                                    hovermode='closest'
                                    )
                }
    
    data = json.loads(children)
    X = np.array(data['X'])
    time = np.array(data['time'])
    output = np.array(data['output'])
    var = data['var']
    layers = data['layers']

    if var == 'Te':
        label, units = 'Temperature', '(K)'
    elif var == 'Pres':
        label, units = 'Pressure', '(GPa)'
    elif var == 'U':
        label, units = 'Particle Velocity', '(km/s)'
    elif var == 'Rho':
        label, units = 'Density', '(g/cc)'
    else:
        label, units = 'Unknown', 'Variable'

    index = np.argmin(abs(time - selected_time))
    traces = []
    annotations = []
    for layer in layers:
        mesh_start = layers[layer]['Mesh Start'] - 1
        if mesh_start < 0:  # check for the first material condition
            mesh_start = 0
        mesh_stop = layers[layer]['Mesh Stop']
        if mesh_stop > len(X) - 1:
            mesh_stop = len(X) - 1

        traces.append(go.Scatter(x=X[mesh_start:mesh_stop], y=output[mesh_start:mesh_stop, index],
                                 name=layers[layer]['Name'],
                                 line=dict(width=4),
                                 )
                      )
        dashed_x = [layers[layer]['X Stop']] * 2
        dashed_y = [0, output.max() + 1]
        traces.append(go.Scatter(x=dashed_x, y=dashed_y,
                                 showlegend=False,
                                 line=dict(color='black', width=1, dash='dot')
                                 )
                      )
        annotations.append(go.layout.Annotation(x=(layers[layer]['X Start'] + layers[layer]['X Stop']) / 2,
                                                y=output.max() * 0.9,
                                                # xref="x",
                                                # yref="y",
                                                text=layers[layer]['Name'],
                                                font=dict(color="black",
                                                          size=16),
                                                showarrow=False
                                                )
                           )
        
    return {'data': traces,
            'layout': go.Layout(title=f'{data["filename"]} {label} Profile',
                                font=dict(size=18),
                                xaxis={'title': 'Lagrangian Distance'},
                                # 'title_font':{'size':24}, 'tickfont':{'size':16} },
                                yaxis={'title': f'{label} {units}'},
                                # 'title_font':{'size':24}, 'tickfont':{'size':16}, 'range':(0, output.max())},
                                margin={'l': 200, 'b': 40, 't': 75, 'r': 200},
                                hovermode='closest',
                                annotations=annotations
                                )
            }


if __name__ == '__main__':
    PORT = 8000
    ADDRESS = '127.0.0.1'
    app.run_server(port=PORT, debug=True)  # host=ADDRESS,
