# third party
import dash_html_components as html
import dash_core_components as dcc
import dash_table_experiments as dt

# project

def retrieve_layout():
    return html.Div([
            # link all css
            # bootstrap
            html.Link(
                rel='stylesheet',
                href='./apps/pipeline_launcher/static/bootstrap.css'),

            # local css
            html.Link(
                rel='stylesheet',
                href='./apps/pipeline_launcher/static/launcher_stylesheet.css'),

            html.Div([

                html.Div([

                    html.H1('Optimus launcher', className='display-2 mx-auto'),

                ], className='row mb-3'),
            html.Div([ # row - col container
                html.Div([ # col
                    html.H1(['Main controls'], className='row mx-auto mb-2'),

                    html.Div([ # row

                        html.Div([
                                html.Div([
                                    dcc.Upload(
                                            id='upload-data',
                                            children=[html.Button(['Upload string data'],
                                                                  className='w-100 btn btn-success')],
                                            className='w-100'),
                                    ], className='mb-2'),


                                html.Div([
                                    html.Button(
                                            id='run-button',
                                            n_clicks=0,
                                            n_clicks_timestamp=0,
                                            children=['Run optimus pipeline'],
                                            className='w-100 btn btn-primary')
                                ], className='mb-2')

                          ], className='col-12'),

                        ], className='row '),


                    html.H2('Configure optimus', className='row mx-auto'),


                    html.H3('Select few parameters'),

                    html.Div([

                    # """
                    # <div class="input-group input-group-sm mb-3">
                    #   <div class="input-group-prepend">
                    #     <span class="input-group-text" id="inputGroup-sizing-sm">Small</span>
                    #   </div>
                    #   <input type="text" class="form-control" aria-label="Small" aria-describedby="inputGroup-sizing-sm">
                    # </div>
                    #
                    # """
                        html.Div([
                            html.Div([
                                html.Span('Stepsize', className='input-group-text')
                            ], className='input-group-prepend'),
                            dcc.Input(id='stepsize', className='form-control'),
                        ], className='input-group mb-2 mx-auto'),
                        html.Div([
                            html.Div([
                                html.Span('  Cutoff', className='input-group-text')
                            ], className='input-group-prepend'),
                            dcc.Input(id='cutoff', className='form-control'),
                        ], className='input-group mb-2 mx-auto'),
                        html.Div([
                            html.Div([
                                html.Span('Distance', className='input-group-text')
                            ], className='input-group-prepend'),
                            dcc.Input(id='distance', className='form-control'),
                        ], className='input-group mb-2 mx-auto'),



                    ], className='row mx-auto'),

                    html.H3('Manual'),


                    html.Div([


                        dcc.Textarea(
                                id='settings',
                                className='form-control mb-2',
                                placeholder='setting:value',
                                style={'height':'175px', 'width':'100%'}
                                ),

                        html.Button(
                                id='remake-optimus',
                                n_clicks=0,
                                children=['Upload Settings'],
                                className='btn btn-success mx-auto',
                                style={'width':'100%','height':'auto'})


                        ], className='row mx-auto text-center mb-2'),
                ], className='col-4'),
                html.Div([
                    html.Div([

                        html.H1('Output log', className='mx-auto'),

                        dcc.Textarea(
                                     id='log',
                                     className='form-control terminal',
                                     placeholder='',
                                     readOnly=True,
                                     style={'height':'400px','width':'100%'})

                        ], className='row'),

                    html.Div([

                        html.H3('Preview of data'),

                        dt.DataTable(
                            rows=[{}],
                            row_selectable=False,
                            filterable=True,
                            sortable=False,
                            max_rows_in_viewport=5,
                            id='my-table')


                        ], className='row')
                ], className='col-8'),
            ], className='row'),
        ], className='container')

    ])
