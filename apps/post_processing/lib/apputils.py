# imports
# base
import operator
import json
from collections import Counter

# third party
import pandas as pd
import dash
import plotly.figure_factory as ff

# project
from .layout import retrieve_layout


# NON-CALLBACK FUNCTIONS REQUIRED FOR THE APP
# -----------------------------------------------------------------------------
class biter(object):
    """A bidirectional iterator which ensures that the index doesn't
    overflow in either direction. Used for generating the next
    cluster on the list.

    Parameters
    ----------
    collection : type
        a `collection` of some sort to iterate through

    Attributes
    ----------
    index : int
        keeps track of the place in the collection
    collection

    """

    def __init__(self, collection=[]):
        self.collection = collection
        self.index = -1

    def next(self):
        """Return the next object in the collection.

        Returns
        -------

        next object in the collection

        """

        try:
            self.index += 1
            return self.collection[self.index]

        except IndexError:

            self.index = len(self.collection) - 1
            return self.collection[self.index]

    def prev(self):
        """return previous object in the collection

        Returns
        -------

        previous object in the collection

        """

        # prevent negative outcomes
        if self.index != 0:
            self.index -= 1

        return self.collection[self.index]

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

def which_button(btn_dict):
    """
    Assesses which button was pressed given the time
    each button was pressed at. It finds the latest
    pressed button and returns the key for it.

    Parameters
    ----------
    btn_dict : dict
        an input dict in the form of {'button name': float(n_clicks_timestamp)}

    Returns
    -------
    dict_key
        Returns whatever the dict keys are for the key that was pressed latest

    """
    return max(btn_dict.items(), key=operator.itemgetter(1))[0]

def preprocess(config):
    """
    A function which uses the config provided to
    create the output files from the original data.
    On top of this it tweaks it slightly.

    Parameters
    ----------
    config : dict
        dictionary containing the config. just needs the paths
        to input and output mainly.

    Returns
    -------
    (list, pd.DataFrame.columns)
        return a list of clusters to keep based on
        the number of items in it as well as the columns in the
        dataframe.

    """

    # read the base data
    df = pd.read_csv(config['data'], encoding=config['encoding'])

    # strip the current labels to remove impact of spaces
    df['current_labels'] = df['current_labels'].str.strip()

    # get the cluster size range and unique cluster names
    keep = [l for l, d in df.groupby(
            'current_labels') if len(d) >= config['min_cluster']]

    # assign new column for future labels
    df['new_labels'] = pd.Series()
    df.loc[~(df['current_labels'].isin(keep)),
           'new_labels'] = 'SKIPPED'

    # save a copy of the data for the further pipeline
    df.to_csv(config['out'], encoding=config['encoding'], index=False)

    return keep, df.columns


def relabeling(df, config, cluster, label='', col='', indices=[]):
    """
    A function that handles relabeling. Used upon each button click
    essentially to relabel the correct cluster items.

    Parameters
    ----------
    df : pd.DataFrame
        dataframe containing the data
    config : dict
        dict object containing the configs for the app
    cluster : str
        a string containing the string name of the cluster
    label : str
        a string label that will be assigned unless col is provided
    col : str
        if col is provided this will be selected as the new label,
        meaning that the whole column will be assigned rather than
        a static string
    indices : list
        a list of indices which the user things should be replaced
        with the new labels

    Returns
    -------
    None
        Returns none as all is saved in a csv file

    """
    # 0 Set up a filter condition for dataframe
    condition = df['current_labels'] == cluster

    if indices:
        # 1. If indices are provided retrieve correct index values
        indices = [n for i, n in enumerate(df[condition].index) if i in indices]
    else:
        # 2. If indices are empty - meaning none were specified, select all
        indices = df[condition].index.tolist()

    # 3. If col was passed asign the relevant column to the label paremeter
    if col:
        label = df.loc[condition, col]

    # 4. Assign the label column
    df.loc[indices, "new_labels"] = label
    df.loc[condition, "new_labels"] = df.loc[condition, "new_labels"].fillna('SKIPPED')

    # 5. Output
    df.to_csv(config['out'], encoding=config['encoding'] index=False)


def draw_table(value, config):
    """
    Draws the table element of the app.

    Parameters
    ----------
    value : str
        which cluster to draw based on. it will
        filter the file loaded in to only the entries where
        current labels are equal to value
    config : dict
        a dict file containing the app settings

    Returns
    -------
    dict
        a dict required by the table object in the main app
        to populated the table with the data.

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

    df = _prepare_for_show(pd.read_csv(config['out'], encoding=config['encoding']))

    df = df[df['current_labels'] == value]

    new_table_figure = df.to_dict('records')

    return new_table_figure


def setup(config_path='config.json'):
    """
    Launch and orchestrate the whole set up process.
    It uses the config function as well as some other functions
    defined above to produce the initial parameters and state
    of the app.

    Parameters
    ----------
    config_path : str
        Path to the config of the app

    Returns
    -------
    (app, dict, list, iterator)
        returns the app, the config file, the clusters list to keep
        and the iterator which will allow navigation through clusters

    """
    # CREATE APP
    app = config_app()

    # LOAD USER CONFIGS
    with open(config_path) as file:
        config = json.load(file)

    # PREPROCESS DATA AND GET APROPRIATE CLUSTER LIST
    keep, cols = preprocess(config)

    # CREATE GENERATOR THROUGH CLUSTERS
    gen = biter(keep)

    # SETUP THE LAYOUT OF THE APP
    app.layout = retrieve_layout(cols, config)

    return app, config, keep, cols, gen
