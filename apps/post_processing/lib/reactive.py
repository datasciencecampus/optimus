# imports
# base
import os

# third party
import pandas as pd
import numpy
import dash_html_components as html
from flask import send_from_directory
from dash.dependencies import Input, Output, State


# project
from .apputils import setup, which_button, relabeling, draw_table



# GENERAL SET UP
# -----------------------------------------------------------------------------

app, config, keep, cols, gen = setup()
@app.callback(
    Output('my-table', 'rows'),
    [Input('my-cluster', 'children')]
)
def trigger(value):
    """
    Redraw the table when the cluster name in the 'my-clusters' object
    changes. Use the name of the cluster to select what will be in the table.

    Parameters
    ----------
    value : str
        something coming in from the children attribute of my-cluster

    Returns
    -------
    dict
        a dict which will populate the table with the right data.

    """
    return draw_table(value, config)


@app.callback(
    Output('my-table', 'selected_row_indices'),
    [Input('my-cluster', 'children')]
)
def clear_selected_indices(value):
    """
    Whenever the cluster changes, the selected rows get
    set to none.

    Parameters
    ----------
    value : str
        cluster name

    Returns
    -------
    []
        returns and empty list which then means non of the
        entries in the table are selected

    """
    return []

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
     State('my-table', 'selected_row_indices')]
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
          indices
          ):
    """Short summary.

    Parameters
    ----------
    rename : timestamp
        timestamp indicating when rename was last pressed
    accept : timestamp
        timestamp indicating when accept was last pressed
    reject : timestamp
        timestamp indicating when reject was last pressed
    accept_dropdown : timestamp
        timestamp indicating when accept a premade dropdown
        was last pressed
    tier_dropdown : timestamp
        timestamp indicating when accept a previous tier from
        dropdown was last pressed
    undo : timestamp
        timestamp indicating when undo was last pressed
    redo : timestamp
        timestamp indicating when redo was last pressed
    cluster : str
        name of the cluster currently being processed
    label : str
        a label value if any that is currently typed into the
        manual renaming
    premade_dropdown_value : str
        what value if any has been selected from the premade
        dropdown
    tier_dropdown_value : str
        what value if any has been selected from the tier dropdown
    indices : list
        list of indices that the user has selected in the table

    Returns
    -------
    str
        a string with the name of the next cluster

    """

    df = pd.read_csv(config['out'], encoding=config['encoding'])
    buttons = {
        'rename': float(rename),
        'accept': float(accept),
        'reject': float(reject),
        'accept_dropdown': float(accept_dropdown),
        'tier_dropdown': float(tier_dropdown),
        'undo': float(undo),
        'redo': float(redo)
    }

    # preload relabel function with arguments

    if label == '' and cluster == '':  # create the first chart
        gen.next()

    else:
        btn = which_button(buttons)

        if btn == 'undo':
            return gen.prev()

        elif btn == 'redo':
            return gen.next()

        elif btn == 'rename':
            relabeling(df=df,
                       config=config,
                       cluster=cluster,
                       label=label,
                       indices=indices)
            if label not in config['options']:
                config['options'].append(label)

        elif btn == 'accept':
            relabeling(df=df,
                       config=config,
                       cluster=cluster,
                       col='current_labels',
                       indices=indices)

            # config['options'].append(
                # df[df['current_labels'] == cluster].loc[0,'current_labels'])

        elif btn == 'reject':
            relabeling(df=df,
                       config=config,
                       cluster=cluster,
                       label='SKIPPED')

        elif btn == 'accept_dropdown':
            relabeling(df=df,
                       config=config,
                       cluster=cluster,
                       label=premade_dropdown_value,
                       indices=indices)
        elif btn == 'tier_dropdown':
            relabeling(df=df,
                       config=config,
                       cluster=cluster,
                       col=tier_dropdown_value,
                       indices=indices)

        return gen.next()


@app.callback(
    Output('progress', 'children'),
    [Input('my-cluster', 'children')]
)
def update_progress(_):
    """
    Update how many clusters have been processed.

    Parameters
    ----------
    _ : str
        a reactive trigger for the update

    Returns
    -------
    str
        string representing what number of clusters have
        been through the process

    """
    df = pd.read_csv(config['out'], encoding=config['encoding'])
    i = len([
        l for l, _ in df.groupby('current_labels')
        if l in keep and _['new_labels'].notnull().all()
    ])
    n = len(keep)
    if i == n:
        return html.H4('All clusters labelled!', className='text-success')
    return f'Classified so far: {i}/{n} ({int((i/n)*100)}%)'


@app.callback(
    Output('my-input', 'value'),
    [Input('my-cluster', 'children')]
)
def clear_rename(_):
    """
    whenever a new cluster is in focus
    reset the renaming field to empty

    Parameters
    ----------
    _ : str
        reactive trigger for the process

    Returns
    -------
    str
        empty string

    """

    return ''


@app.callback(
    Output('my-dropdown', 'value'),
    [Input('my-cluster', 'children')]
)
def clear_name_dropdown(_):
    """
    whenever a new cluster is in focus reset
    the premade name dropdown to empty again

    Parameters
    ----------
    _ : str
        reactive trigger for the process

    Returns
    -------
    str
        sets the value back to the default
        which is SKIPPED. this is because
        if people press done with nothing
        selected this skipped value is
        assigned

    """
    return 'SKIPPED'


@app.callback(
    Output('tier-dropdown', 'value'),
    [Input('my-cluster', 'children')]
)
def clear_tier_dropdown(_):
    """
    whenever a new cluster is in focus reset
    the tier dropdown to empty again

    Parameters
    ----------
    _ : str
        reactive trigger for the process

    Returns
    -------
    str
        empty string
    """
    return ''


@app.callback(
    Output('my-dropdown', 'options'),
    [Input('my-cluster', 'children')],
)
def add_to_dropdown(_):
    """
    Update the dropdown selection options to
    included the latest cluster labels added
    through renaming or accepting.

    Parameters
    ----------
    _ : str
        reactive trigger coming from my-cluster - children
        attribute

    Returns
    -------
    list
        a list with a dictionary of values and labels
        which will populate the dropdown as default values

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
