#imports
# base
import os
import json
from time import gmtime, strftime
from collections import Counter

# third party
import pandas as pd
import dash
import dash_html_components as html
import dash_core_components as dcc
import plotly.figure_factory as ff
from flask import send_from_directory
from dash.dependencies import Input, Output, State

# project
from apputils import config_app, preprocess, biter, relabeling, which_button


# GENERAL SET UP
# -----------------------------------------------------------------------------

# GET START TIME
curr_time = f"The server was started at: {strftime('%H:%M:%S',gmtime())}"

# CREATE APP
app = config_app()

# LOAD USER CONFIGS
with open('config.json') as file:
    config = json.load(file)

# PREPROCESS DATA AND GET APROPRIATE CLUSTER LIST
keep, cols = preprocess(config)

# CREATE GENERATOR THROUGH CLUSTERS
gen = biter(keep)


# APP LAYOUT
# -----------------------------------------------------------------------------

app.layout = html.Div([
    html.Title('OPTIMUS'),
    # link all css
    # bootstrap
    html.Link(
        rel='stylesheet',
        href='/static/bootstrap.css'),

    # local css
    html.Link(
        rel='stylesheet',
        href='/static/stylesheet.css'),

    # placeholder for the back button
    html.Div([

    ],
    style={"display": 'none'},
    id='undo-state'),

    html.Div([

    ],
    style={"display": 'none'},
    id='previous-label'),

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

                html.P('Pick earlier tier as the new label', className='mb-0'),

                dcc.Dropdown(id='tier-dropdown',
                             options=[{'label': l, 'value': l}
                                      for l in cols if 'tier_' in l],
                             value='SKIPPED',
                             className='mb-1'
                             ),

                html.Button('Done',
                            id='pick-tier',
                            n_clicks_timestamp=0,
                            className="btn btn-secondary mb-1")
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


# APP CALLBACK FUNCTIONS
# -----------------------------------------------------------------------------
def draw_table(value):
    """
    This function creates a table using the plotly module.
    """

    def _prepare_for_show(frame):
        frame = frame.drop('new_labels', axis=1)
        tiers = list(frame.filter(like='tier').columns)
        tier_dict = {t:float(t[-1]) for t in tiers}

        # pick only the top 2 tiers
        save_tiers = [col for col,_ in
                        Counter(tier_dict).most_common(config['tiers'])]

        # reorder and trim
        frame = frame[['current_labels','original'] + save_tiers]

        return frame

    df = _prepare_for_show(pd.read_csv(config['out']))

    df = df[df['current_labels'] == value]

    # table colorscale
    colorscale = [[0, '#000000'],[.5, '#e2e2e2'],[1, '#ffffff']]

    new_table_figure = ff.create_table(df, colorscale=colorscale)
    return new_table_figure

@app.callback(
    Output('my-table', 'figure'),
    [Input('my-cluster', 'children')]
)
def trigger(value):
    """
    Redraw the table when the cluster name in the 'my-clusters' object
    changes. Use the name of the cluster to select what will be in the table.
    """
    return draw_table(value)

@app.callback(
    Output('my-cluster', 'children'),
    [Input('rename', 'n_clicks_timestamp'),
     Input('accept', 'n_clicks_timestamp'),
     Input('reject', 'n_clicks_timestamp'),
     Input('pick-name', 'n_clicks_timestamp'),
     Input('pick-tier', 'n_clicks_timestamp'),
     Input('undo', 'n_clicks_timestamp'),
     Input('redo', 'n_clicks_timestamp')],
    [State('my-cluster', 'children'),
     State('my-input', 'value'),
     State('my-dropdown', 'value'),
     State('tier-dropdown', 'value'),
     State('my-cluster', 'children')]
)
def label(rename,
          accept,
          reject,
          accept_dropdown,
          tier_dropdown,
          undo,
          redo,
          cluster,
          label,
          premade_dropdown_value,
          tier_dropdown_value,
          current_cluster
          ):
    df = pd.read_csv(config['out'])

    buttons = {
        'rename': float(rename),
        'accept': float(accept),
        'reject': float(reject),
        'accept_dropdown': float(accept_dropdown),
        'tier_dropdown': float(tier_dropdown),
        'undo':float(undo),
        'redo':float(redo)
    }

    if label == '' and cluster == '':  # create the first chart
        next(gen)

    else:
        btn = which_button(buttons)

        if btn == 'undo':
            return gen.prev()

        elif btn == 'redo':
            return next(gen)

        elif btn == 'rename':
            relabeling(df, config, cluster,  label)
            if label not in config['options']:
                config['options'].append(label)

        elif btn == 'accept':
            new_label = df['current_labels']
            relabeling(df, config, cluster,  new_label)
            for label in new_label[df['current_labels'] == current_cluster].unique():
                if label not in config['options']:
                    config['options'].append(label)
        elif btn == 'reject':
            relabeling(df, config, cluster,  'SKIPPED')

        elif btn == 'accept_dropdown':
            relabeling(df, config, cluster,  premade_dropdown_value)

        elif btn == 'tier_dropdown':
            new_label = df[tier_dropdown_value]
            relabeling(df, config, cluster,  new_label)
            for label in new_label[df['current_labels'] == current_cluster].unique():
                if label not in config['options']:
                    config['options'].append(label)

        try:
            return next(gen)
        except StopIteration:
            return 'FINISHED!'


@app.callback(
    Output('progress', 'children'),
    [Input('my-cluster', 'children')]
)
def update_progress(_):
    """
    Update the progress tracker showing how many clusters were processed
    until now.
    """
    df = pd.read_csv(config['out'])
    i = len([
        l for l, _ in df.groupby('current_labels')
        if l in keep and _['new_labels'].notnull().all()
    ])
    n = len(keep)
    return f'Currently working on cluster: {i}/{n}'


@app.callback(
    Output('my-input', 'value'),
    [Input('my-cluster', 'children')]
)
def clear_rename(_):
    """
    Clear the rename field after each iteration. Triggered by a change in
    'my-cluster' children attribute.
    """
    return ''


@app.callback(
    Output('my-dropdown', 'value'),
    [Input('my-cluster', 'children')]
)
def clear_name_dropdown(_):
    """
    Clear the dropdown and set its value to SKIPPED. This is needed if someone
    decides to skip the cluster and clicks pick name.
    """
    return 'SKIPPED'


@app.callback(
    Output('tier-dropdown', 'value'),
    [Input('my-cluster', 'children')]
)
def clear_tier_dropdown(_):
    """
    Clear the tier dropdown value. Set it to an empty string.
    """
    return ''

@app.callback(
    Output('my-dropdown', 'options'),
    [Input('my-cluster', 'children')],
)
def add_to_dropdown(_):
    """
    Add a new entry to the options of a dropdown. Returns a list which
    then gets assigned to 'my-dropdown' options attribute.
    """
    return [{'label': string, 'value': string}
            for string in sorted(config['options']) if string != '']


# needed to serve local css
@app.server.route('/static/<path:path>')
def static_file(path):
    """
    This is required to serve local CSS files. This uses the flask
    backend upon which dash is built to allow dash to load local css and
    other files.
    """
    static_folder = os.path.join(os.getcwd(), 'static')
    print(f'Serving stylesheets from: {static_folder}')
    return send_from_directory(static_folder, path)


# Boilerplate
if __name__ == '__main__':
    app.run_server(debug=True)
