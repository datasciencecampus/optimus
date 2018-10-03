# third party
import dash_html_components as html
import dash_core_components as dcc
import dash_table_experiments as dt

def retrieve_layout(cols, config):

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

                # output path

                html.P(f"Output will be saved saved in: {config['out']}"),

                # progress tracker
                html.Div(id='progress')

            ], className='col-2'),

            # cluster name
            html.Div([
                html.H1('Current cluster: '),
                html.P(id='my-cluster', className='display-3 text-danger')
                ], className='col-5'),

            html.Div([
                html.Div([
                    html.Img(src='/static/color_logo.png',
                    className='img-fluid w-75 mx-auto d-block')
                ], className='h-100 w-100 mx-auto')
            ], className='col-5 container'),



        ], className="row mb-3 p-1 border-bottom border-secondary"),


        html.Div([

            html.Div([
                html.Div([
                    html.Button('<',
                        id='undo',
                        n_clicks_timestamp=0,
                        className="btn btn-warning mx-1 w-25"),

                    html.Button('>',
                        id='redo',
                        n_clicks_timestamp=0,
                        className="btn btn-warning mx-1 w-25"),

                ], className='mx-auto w-75'),

            ], className='row text-center'),


            html.Div([

                html.Div([
                    html.Div([

                        html.P('Accept or reject the predicted cluster label')],

                     className='row w-100 h-50 mx-0'),

                    html.Div([

                        html.Button('Skip',
                                id='reject',
                                n_clicks_timestamp=0,
                                className="btn btn-danger h-100 w-50"),

                        html.Button('Accept',
                                id='accept',
                                n_clicks_timestamp=0,
                                className="btn btn-warning h-100 w-50"),

                    ], className='row h-50 w-100 mx-0')

                ], className='col-3'),

                html.Div([

                    html.Div([

                        html.P('Provide a new label manually', className='mb-0'),

                    ],className='row w-100 h-25 mx-0'),

                    html.Div([

                        html.Div([
                            dcc.Input(id='my-input',
                                  placeholder='Enter a value...',
                                  type='text',
                                  value='',
                                  className='form-control w-100 h-100'
                                  ),
                            ], className='h-40 w-100 mb-0'),

                        html.Div([
                            html.Button('Done',
                                    id='rename',
                                    n_clicks_timestamp=0,
                                    className="btn btn-secondary h-100 w-100")
                            ],className="h-50 w-100"),

                    ],className='row w-100 h-75 mx-0'),

                ], className='col-3'),

                # dropdown for cluster names
                html.Div([
                    html.Div([

                        html.P('Pick a label from a predefined list', className='mb-0'),

                    ],className='row w-100 h-25 mx-0'),

                    html.Div([

                        html.Div([
                            html.Div([
                                dcc.Dropdown(id='my-dropdown',
                                             options=[{'label': l, 'value': l}
                                                      for l in config['options']],
                                             value='SKIPPED',
                                             className=''                                             ),
                            ], className='h-50 w-100'),

                            html.Div([
                                html.Button('Done',
                                            id='pick-name',
                                            n_clicks_timestamp=0,
                                            className="btn btn-secondary h-100 w-100")
                                    ],className="h-50 w-100"),

                        ],className='col-12 px-0'),

                    ],className='row w-100 h-75 mx-0'),


                ], className='col-3'),

                # tier dropdown
                html.Div([

                    html.Div([
                        html.P('Select correct labels from previous tier:', className='mb-0'),
                    ],className='row w-100 h-25 mx-0'),

                    html.Div([
                        html.Div([
                            dcc.Dropdown(id='tier-dropdown',
                                         options=[{'label': l, 'value': l}
                                                  for l in cols if 'tier_' in l],
                                         value='SKIPPED',
                                         className=''
                                         ),
                        ], className='h-50 w-100'),

                        html.Div([
                            html.Button('Done',
                                        id='pick-tier',
                                        n_clicks_timestamp=0,
                                        className="btn btn-secondary h-100 w-100"),
                        ],className="h-50 w-100"),

                    ],className='row w-100 h-75 mx-0'),

                ], className='col-3'),

        ], className='row mb-3 mt-3'),

        html.Div([
            # table
            dt.DataTable(
                rows=[{}], # initialise the rows
                row_selectable=True,
                filterable=True,
                sortable=False,
                selected_row_indices=[],
                max_rows_in_viewport=150,
                id='my-table')],
                style={'width': '100%'},
                className='row h-100 mx-0')
            ])

    ], className='px-4')
