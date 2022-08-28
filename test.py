from plotly.subplots import make_subplots
import plotly.graph_objects as go
import numpy as np

fig = make_subplots(rows=1, cols=2, subplot_titles = ('Subplot (1,1)', 'Subplot(1,2)'))

#
fig.add_trace(go.Scatter(
          x= [-2.0, -1.0, 0.01, 1.0, 2.0, 3.0],
          y= [4, 1, 1, 1, 4, 9],
          mode = 'markers+lines',
          hoverinfo='name',
          legendgroup= 'f1',
          line_color= 'rgb(255, 79, 38)',
          name= 'f1',
          showlegend= True), row=1, col=1)

#
fig.add_trace(go.Scatter(
          x= [-2.0, -1.0, 0.01, 1.0, 2.0, 3.0],
          y= [3, 8.3, 5.5, 4.24, 6.7, 7],
          mode = 'markers+lines',
          hoverinfo='name',
          legendgroup= 'f1p',
          line_color= 'rgb(79, 38, 255)',
          name= 'f1p',
          showlegend= True), row=1, col=1)


fig.add_trace(go.Heatmap(z=np.random.rand(4, 10)), row=1, col=2)


# Define frames
number_frames = 100
frames = [dict(
    name=k,
    data=[go.Scatter(y=4 + 5 * np.random.rand(6)),  # update the trace 1 in (1,1)
          go.Scatter(y=2 + 6 * np.random.rand(6)),  # update the second trace in (1,1)
          go.Heatmap(z=np.random.rand(4,10))  # update the trace in (1,2)
          ],
    traces=[0, 1, 2] 
) for k in range(number_frames)]


# Play button
updatemenus = [dict(type='buttons',
                    buttons=[dict(label='Play',
                                  method='animate',
                                  args=[[f'{k}' for k in range(number_frames)],
                                        dict(frame=dict(duration=500, redraw=True),
                                             transition=dict(duration=0),
                                             easing='linear',
                                             fromcurrent=True,
                                             mode='immediate'
                                             )]),
                             dict(label='Pause',
                                  method='animate',
                                  args=[[None],
                                        dict(frame=dict(duration=0, redraw=False),
                                             transition=dict(duration=0),
                                             mode='immediate'
                                             )])
                             ],
                    direction='left',
                    pad=dict(r=10, t=85),
                    showactive=True, x=0.1, y=0, xanchor='right', yanchor='top')
               ]


# Slider
sliders = [{'yanchor': 'top',
            'xanchor': 'left',
            'currentvalue': {'font': {'size': 16}, 'prefix': 'Frame: ', 'visible': True, 'xanchor': 'right'},
            'transition': {'duration': 0, 'easing': 'linear'},
            'pad': {'b': 10, 't': 50},
            'len': 0.9, 'x': 0.1, 'y': 0,
            'steps': [{'args': [[k], {'frame': {'duration': 0, 'easing': 'linear', 'redraw': False},
                                      'transition': {'duration': 0, 'easing': 'linear'}}],
                       'label': k, 'method': 'animate'} for k in range(number_frames)
                      ]}]


fig.update(frames=frames),
fig.update_layout(updatemenus=updatemenus,
                  sliders=sliders)
fig.show() 

