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
    """
    bidirectional mock-iterator made for the purpose of crawling
    through the clusters
    """
    def __init__(self, collection=['one','two','three','four']):
        self.collection = collection
        self.index = -1

    def next(self):

        try:
            self.index += 1
            return self.collection[self.index]

        except IndexError:

            self.index = len(self.collection) - 1
            return self.collection[self.index]

    def prev(self):
        # prevent negative outcomes
        if self.index != 0:
            self.index -= 1

        return self.collection[self.index]

def config_app():
    """
    A simple wrapper that just returns a configured
    dash app object.
    """
    # DASH CONFIGSs
    app = dash.Dash()

    # settings to serve css locally
    app.css.config.serve_locally = True
    app.scripts.config.serve_locally = True
    app.title = 'Optimus'

    return app

def which_button(btn_dict):
    return max(btn_dict.items(), key=operator.itemgetter(1))[0]

def preprocess(config):
    """
    A function which uses the config provided to
    create the output files from the original data.
    On top of this it tweaks it slightly.
    """
    # read the base data
    df = pd.read_csv(config['data'])

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
    df.to_csv(config['out'], index=False)

    return keep, df.columns


def relabeling(df, config, cluster, label):
    df.loc[(df['current_labels'] == cluster), 'new_labels'] = label
    # this next line ensure that any entries who happen to have the same
    # suggested label get classfied
    if config['smart_labeling']:
        df.loc[(df['current_labels'] == label), 'new_labels'] = label
    df.to_csv(config['out'], index=False)

def draw_table(value, config):
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


def setup(config_path='config.json'):
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
