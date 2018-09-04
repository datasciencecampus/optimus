# base
from time import gmtime, strftime

# third party
import dash_html_components as html
import dash_core_components as dcc

def retrieve_layout(cols, config):
    # GET START TIME
    curr_time = f"The server was started at: {strftime('%H:%M:%S',gmtime())}"

    return html.Div([
        # link all css
        # bootstrap
        html.Link(
            rel='stylesheet',
            href='/static/bootstrap.css'),

        # local css
        html.Link(
            rel='stylesheet',
            href='/static/stylesheet.css'),

        html.Div([

            html.Div([

                html.H3('Information:'),

                # time started
                html.P(curr_time),

                # output path

                html.P(f"Output will be saved saved in: {config['out']}"),

                # progress tracker
                html.Div(id='progress')

            ], className='col-2'),

            # cluster name
            html.Div([
                html.H1('Current cluster: '),
                html.P(id='my-cluster', className='display-3')
                ], className='col-5'),

            html.Div([
                html.Img(src='/static/black_logo.jpg',
                className='img-fluid')
            ], className='col-5 container'),



        ], className="row mb-3 p-1 border-bottom border-secondary"),


        html.Div([
            html.Div([

                html.Button('<',
                    id='undo',
                    n_clicks_timestamp=0,
                    className="btn btn-secondary mb-1"),

                html.Button('>',
                    id='redo',
                    n_clicks_timestamp=0,
                    className="btn btn-secondary mb-1"),

                html.Div([

                    html.P('Accept or reject the predicted cluster label', className='mb-0'),

                    html.Button('Accept',
                            id='accept',
                            n_clicks_timestamp=0,
                            className="btn btn-warning mb-1"),

                    html.Button('Skip',
                            id='reject',
                            n_clicks_timestamp=0,
                            className="btn btn-danger mb-1 ml-1"),

                    html.P('Provide a new label manually', className='mb-0'),

                    html.Div([
                        dcc.Input(id='my-input',
                              placeholder='Enter a value...',
                              type='text',
                              value='',
                              className='form-control'
                              ),
                        ], className='mb-1'),

                    html.Button('Done',
                                id='rename',
                                n_clicks_timestamp=0,
                                className="btn btn-secondary mb-1"),


                ]),

                # dropdown for cluster names
                html.Div([

                    html.P('Pick a label from a predefined list', className='mb-0'),

                    dcc.Dropdown(id='my-dropdown',
                                 options=[{'label': l, 'value': l}
                                          for l in config['options']],
                                 value='SKIPPED',
                                 className='mb-1'
                                 ),

                    html.Button('Done',
                                id='pick-name',
                                n_clicks_timestamp=0,
                                className="btn btn-secondary mb-1")
                ]),

                # tier dropdown
                html.Div([

                    html.P('Select correct labels from previous tier:', className='mb-0'),

                    dcc.Dropdown(id='tier-dropdown',
                                 options=[{'label': l, 'value': l}
                                          for l in cols if 'tier_' in l],
                                 value='SKIPPED',
                                 className='mb-1'
                                 ),

                    html.Button('Done',
                                id='pick-tier',
                                n_clicks_timestamp=0,
                                className="btn btn-secondary mb-1"),


                    dcc.Checklist(
                        id='tier-checklist',
                        options=[],
                        values=[],
                        labelStyle={'display':'block'}
                        )

                ]),


            ], className='col-2'),

            # table
            dcc.Graph(
                id='my-table',
                config={
                    'staticPlot': True,
                    'displayModeBar': True
                }, className='col-10')

        ], className='row pt-0 mt-0'),



    ], className='')
