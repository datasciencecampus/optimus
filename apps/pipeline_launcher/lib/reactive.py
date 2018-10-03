# TODO: explore multiprocessing using gunicorn syntax
# TODO: explore adding bokeh tables rather than dash tables
# TODO: instead of upload settings make them get picked up automaticall if the box is not empty
# TODO: store button last clicked in a invisible div
# TODO: store layouts in a dict with proper tab-1 and tab-2 keys for less code access
# TODO: stop the thing advancing everytime i switch tabs or reset where it is each time
#imports
# base
import os
import pickle

# third party
import pandas as pd
import fastText as ft
import dash
import dash_html_components as html
import dash_core_components as dcc
from flask import send_from_directory
from dash.dependencies import Input, Output, State

# project
from apps.pipeline_launcher.lib.apputils import setup, parse_settings, parse_upload_contents, run_optimus


# GENERAL SET UP
# -----------------------------------------------------------------------------

app, layout, o, Optimus = setup()

# SET UP DEFAULT APP
# This is required as some callback id's don't exist until you swap tabs
app.config['suppress_callback_exceptions']=True

# A starting layout that will be populated - needed for tabs
app.layout = layout

# a simplistic workaround to ensure that when running the app
# from the optimus root directory it still functions
# containerised within the pipeline launcher folder
# with the exception of normal optimus outputs
path = './apps/pipeline_launcher/'

# APP CALLBACK FUNCTIONS - The reactive brain of the app.
# -----------------------------------------------------------------------------
# TABS CALLBACK
# A callback required to populate the tabs with content

# OPTIMUS CALLBACKS
@app.callback(
    Output('my-table', 'rows'),
    [Input('upload-data', 'contents'),
     Input('upload-data', 'filename'),
     Input('log','value')])
def preview_upload(contents, filename, log):
    """
    A function to plot the data

    Parameters
    ----------
    contents : str
        str containing encoded data that has just
        been uploaded
    filename : str
        a string file containing the filename that
        was just loaded
    log : str
        here to act as a reactive trigger

    Returns
    -------
    list
        a list with a dict inside containing
        the parsed records from the uploaded
        file. this gets passed onto rows

    """

    if contents != None:

        return parse_upload_contents(contents, filename)

    else:

        return [{}]

@app.callback(
    Output('log','value'),
    [Input('run-button','n_clicks')]
)
def optimus(_):
    """
    This waits for a run button click and
    sends off optimus to do its work.

    Parameters
    ----------
    _ : int
        mainly a trigger for work

    Returns
    -------
    str
        returns the log outputs of
        optimus or error markers

    """
    try:
        if _ != 0:
            with open(path+'o','rb') as f:
                o = pickle.load(f)
            run_optimus(pd.read_csv(path+'uploaded_data.csv', header=None).iloc[:,0], o)
            with open(path+'log.txt', 'r') as f:
                return f.read()
        else:
            return ''
    except ModuleNotFoundError:
        return 'ModuleNotFoundError'

@app.callback(
    Output('settings','placeholder'),
    [Input('remake-optimus', 'n_clicks')],
    [State('settings','value'),
     State('stepsize','value'),
     State('cutoff','value'),
     State('distance','value'),
     State('model','value'),
    ]
)
def ingest_settings(_,
                    settings_field,
                    stepsize,
                    cutoff,
                    distance,
                    model):
    """
    Short summary.

    Parameters
    ----------
    _ : int
        mainly used to listen for
        the upload-settings button click
    settings_field : str
        string containing the settings
        to be parsed and passed onto optimus
    stepsize : str
        a specific value given for stepsize
    cutoff : str
        a specific value given for cutoff
    distance : str
        a specific value given for distance

    Returns
    -------
    str
        returns the settings placeholder string

    """

    def dealwithsettings(settings_field,
                          **kwargs):

        kwargs = {k:int(v) for k,v in kwargs.items() if v != None}

        if settings_field:
            return {**kwargs, **parse_settings(settings_field)}

        return kwargs

    if _ != 0:


        o = Optimus(
            config_path='config.json',
            data=path+'uploaded_data.csv',
            **dealwithsettings(settings_field,
                              stepsize=stepsize,
                              distance=distance,
                              cutoff=cutoff),
            model=model
            )

        with open(path+'o','wb+') as f:
            pickle.dump(o,f)

        return """Enter settings like so: 'setting:value' and separate multiple settings with a comma. \n\nNote: do not leave comma at the end."""

    else:
        return """Enter settings like so: 'setting:value' and separate multiple settings with a comma. \n\nNote: do not leave comma at the end."""

# needed to serve local css
@app.server.route('/apps/pipeline_launcher/static/<path:path>')
def static_file(path):
    """
    This is required to serve local CSS files. This uses the flask
    backend upon which dash is built to allow dash to load local css and
    other files.
    """
    # static_folder = os.path.join(os.getcwd(), 'static')
    static_folder = './apps/pipeline_launcher/static'
    print(f'Serving stylesheets from: {static_folder}')
    return send_from_directory(static_folder, path)
