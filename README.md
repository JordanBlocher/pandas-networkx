        html.Div(
            [
                dcc.RadioItems(
                            ['Noise'], 
                            id='radio-items', 
                            inline=True,
                            value=params['noise']
                            )
            ],
          style={'display': 'grid', 'grid-template-columns': '10% 35% 10% 35%'}
        ),
        html.Div(
            [
                html.Label('nbuyers', style={'text-align': 'right'}),
                dcc.Slider(
                    id='n-buyers',
                    min=0,
                    max=100,
                    value=params['nbuyers'], 
                    tooltip={'placement': 'bottom'}
                ),
                html.Label('nsellers', style={'text-align': 'right'}),
                dcc.Slider(
                    id='n-sellers',
                    min=0,
                    max=100,
                    value=params['nsellers'],
                    tooltip={'placement': 'bottom'}
                )
            ],
            style={'display': 'grid', 'grid-template-columns': '10% 35% 10% 35%'}
        ),
        html.Div(id='hidden-div')  
@app.callback(
    Output('hidden-div', 'children'),[
    Input('n-buyers', 'value'), Input('n-sellers', 'value'),
    Input('radio-items', 'value')
    ]
)
def update_output(n, m, x):
    global nbuyers, nsellers, noise
    nbuyers = n
    nsellers = m
    noise = x
