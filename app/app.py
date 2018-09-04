#imports
# base
import os
import json
from collections import Counter

# third party
import pandas as pd
import dash
import plotly.figure_factory as ff
from flask import send_from_directory
from dash.dependencies import Input, Output, State

# project
from apputils import config_app, preprocess, biter, relabeling, which_button
from layout import retrieve_layout

# GENERAL SET UP
# -----------------------------------------------------------------------------

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

app.layout = retrieve_layout(cols, config)

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
     State('my-cluster', 'children'),
     State('tier-checklist', 'values')]
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
          current_cluster,
          tier_checklist_values
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
            new_label = df[tier_dropdown_value].map(
                        lambda label: label if label in tier_checklist_values
                        else 'SKIPPED')
            relabeling(df, config, cluster,  new_label)
            for label in new_label[df['current_labels'] == current_cluster].unique():
                if (label not in config['options'] and
                   label != 'SKIPPED' and label in tier_checklist_values):
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

@app.callback(
    Output('tier-checklist', 'options'),
    [Input('tier-dropdown', 'value')],
    [State('my-cluster', 'children')]
)
def get_checklist(tier, cluster):

    if tier != '':
        df = pd.read_csv(config['out'])
        unique = df.loc[df['current_labels'] == cluster, tier].unique()

        return [{'label':val, 'value':val} for val in unique]

    else:

        return []

@app.callback(
    Output('tier-checklist', 'values'),
    [Input('tier-checklist', 'options')],
    [State('tier-checklist', 'options')]
)
def tick_all(_, options):

    return [d['value'] for d in options]



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
