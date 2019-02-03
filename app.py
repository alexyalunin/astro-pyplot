import dash
import dash_html_components as html
import dash_core_components as dcc
from sklearn import preprocessing
import numpy as np
from pyrao import BSAData
from plotly.graph_objs import Layout, Scatter, Figure, Marker, Scattergl
from plotly.graph_objs.layout import YAxis, Annotation, Font
from plotly.graph_objs.layout.annotation import Font

# import bokeh
# import pandas as pd
# import numpy as np
# from datetime import datetime, timedelta


data = BSAData()

path1 = '070712_05_00.pnt'
path2 = 'eq_1_6b_20120706_20130403.txt'
path3 = './output/'

data.convert([path1, path2, path3])  # Read and write 48 .fil files from
data.convert([path1, path2, path3], limits=[10, 1000],
             beams=[4, 9])  # Read and write beams #5 and #10 with observations from 11-th to 1000-th

data_orig = preprocessing.scale(data.data[:, :, 0])

n_channels = 48
ch_names = [str(i) for i in range(1, n_channels + 1)]

data = data_orig.transpose()[:n_channels, :]
times = np.array(np.linspace(0, 24, 990))

step = 1. / n_channels
kwargs = dict(domain=[1 - step, 1], showticklabels=False, zeroline=False, showgrid=False)

# create objects for layout and traces
layout = Layout(yaxis=YAxis(kwargs), showlegend=False)
traces = [Scattergl(x=times, y=data.T[:, 0])]

# loop over the channels
for ii in range(1, n_channels):
    kwargs.update(domain=[1 - (ii + 1) * step, 1 - ii * step])
    layout.update({'yaxis%d' % (ii + 1): YAxis(kwargs), 'showlegend': False})
    traces.append(Scattergl(x=times, y=data.T[:, ii], yaxis='y%d' % (ii + 1)))

# add channel names using Annotations
annotations = list([Annotation(x=-0.06, y=0, xref='paper', yref='y%d' % (ii + 1),
                               text=ch_name, font=Font(size=9), showarrow=False)
                    for ii, ch_name in enumerate(ch_names)])

layout.update(annotations=annotations)

# set the size of the figure and plot it
layout.update(autosize=False, width=1000, height=800)
# fig = Figure(data=traces, layout=layout)
# py.iplot(fig, filename='shared xaxis')





external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
app.layout = html.Div([
    html.Div(),
    html.Button('Clear', id='button'),
    html.Div(id='output-container-button'),
    dcc.Graph(
        id='graph-id',
        figure={
            'data': traces,
            'layout': layout
        }
    )
])

def mathFunction(_data):
    for i, n in enumerate(_data):
        if n > 1. or n < -1.:
            _data[i] = 0.
    return _data

@app.callback(
    dash.dependencies.Output('graph-id', 'figure'),
    [dash.dependencies.Input('button', 'n_clicks')])
def update_output(n_clicks):
    print(n_clicks)
    if n_clicks == 0 or n_clicks is None:
        return {
            'data': traces,
            'layout': layout
        }
    else:
        data = data_orig.transpose()[:n_channels, :]

        step = 1. / n_channels
        kwargs = dict(domain=[1 - step, 1], showticklabels=False, zeroline=False, showgrid=False)

        # create objects for layout and traces
        layout = Layout(yaxis=YAxis(kwargs), showlegend=False)
        traces = [Scattergl(x=times, y=data.T[:, 0])]

        # loop over the channels
        for ii in range(1, n_channels):
            kwargs.update(domain=[1 - (ii + 1) * step, 1 - ii * step])
            layout.update({'yaxis%d' % (ii + 1): YAxis(kwargs), 'showlegend': False})
            data_ = mathFunction(data.T[:, ii])
            traces.append(Scattergl(x=times, y=data_, yaxis='y%d' % (ii + 1)))

        # add channel names using Annotations
        annotations = list([Annotation(x=-0.06, y=0, xref='paper', yref='y%d' % (ii + 1),
                                       text=ch_name, font=Font(size=9), showarrow=False)
                            for ii, ch_name in enumerate(ch_names)])

        layout.update(annotations=annotations)

        # set the size of the figure and plot it
        layout.update(autosize=False, width=1000, height=800)

        return {
                'data': traces,
                'layout': layout
                }


if __name__ == '__main__':
    app.run_server(debug=False)
