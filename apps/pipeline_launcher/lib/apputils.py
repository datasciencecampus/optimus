# imports
# base
import os
import sys
import operator
import json
import base64
import datetime
import io
import functools
import pickle
from collections import Counter


# third party
import pandas as pd
import dash
import plotly.figure_factory as ff
import dash_html_components as html
import dash_core_components as dcc
import dash_table_experiments as dt
# project
from .layout import retrieve_layout

# Helps with importing optimus
from optimus import Optimus


# a simplistic workaround to ensure that when running the app
# from the optimus root directory it still functions
# containerised within the pipeline launcher folder
# with the exception of normal optimus outputs
path = './apps/pipeline_launcher/'


# NON-CALLBACK FUNCTIONS AND CLASSES REQUIRED FOR THE APP
# -----------------------------------------------------------------------------

def config_app():
    """
    Configure the APP in the required manner.
    Enables local css and js as well as sets page title to Optimus.

    Returns
    -------
    dash_app
        A configured dash app

    """

    # DASH CONFIGSs
    app = dash.Dash()

    # settings to serve css locally
    app.css.config.serve_locally = True
    app.scripts.config.serve_locally = True
    app.title = 'Optimus'

    return app

def parse_settings(settings):
    """
    Parse the free-text entry field and
    create a dictionary of parameters for
    optimus

    Parameters
    ----------
    settings : str
        a string containing settings to be past to
        optimus

    Returns
    -------
    dict
        a dictionary full of parameters
        not unlike a kwargs

    """
    settings = settings.split(',')
    settings = [s.split(':') for s in settings]
    def _clean(s):
        s = s.strip().lower()
        try:
            s = eval(s)
        except:
            pass
        return s
    settings = [list(map(_clean, l)) for l in settings]
    return {l[0]:l[1] for l in settings}

def parse_upload_contents(contents, filename):
    """
    This parses the uploaded datset and turns it into a
    pandas dataframe which is the saved to perpetuate
    state.

    It returns a dict containing all the records needed
    to preview the data using dash table experiments
    tables embedded in the app.

    Parameters
    ----------
    contents : an encoded string
        the uploaded file
    filename : str
        the uploaded file name

    Returns
    -------
    dict
        dict containing the uploaded data

    """
    content_string = contents.split(',')[1]
    decoded = base64.b64decode(content_string)
    try:
        if 'csv' in filename:
            # Assume that the user uploaded a CSV file
            df = pd.read_csv(
                io.StringIO(decoded.decode('utf-8')), header=None)
        elif 'xls' in filename:
            # Assume that the user uploaded an excel file
            df = pd.read_excel(io.BytesIO(decoded), header=None)
        df.to_csv(path+'uploaded_data.csv', header=None, index=None)
        df.columns = ['DATA']
    except Exception as e:
        return [{}]

    return df.to_dict('records')

def setup():
    """
    A set up procedure for the app.

    Returns
    -------
    tuple
        It returns (dash.app, app.layout,
        optimus instance, Optimus module)

    """

    # CREATE APP
    app = config_app()

    # Create persistant optimus object
    o = Optimus(
            config_path='config.json',
            data=path+'uploaded_data.csv')

    with open(path+'o','wb+') as f:
        pickle.dump(o,f)


    return app, retrieve_layout(), o, Optimus

def save_log(filename):
    """
    A decorator which grabs the outputs of a function
    and saves it into a file based on the provided filename

    Parameters
    ----------
    filename : str
        path/name of the file which will act as a log

    Returns
    -------
    func
        decorated function

    """
    def decorator(func):
        def wrapper(*args, **kwargs):

            with open(filename, 'w+') as f:
                orig_stdout = sys.stdout
                sys.stdout = f
                out = func(*args, **kwargs)
                sys.stdout = orig_stdout

            return out
        return wrapper
    return decorator

@save_log(path+'log.txt')
def run_optimus(series, o):
    """
    A wrapper for the o.__call__ method
    which provides several parameters.

    Parameters
    ----------
    series : pandas.core.series.Series
        a pandas series with data
    o : Optimus
        an optimus object

    Returns
    -------
    None
        no return, but file is saved as
        save_csv is set to True

    """
    o(series, save_csv=True, full = True, verbose = True, runKNN=False)
