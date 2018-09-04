# imports
# base
import operator
# third party
import pandas as pd
import dash

# NON-CALLBACK FUNCTIONS REQUIRED FOR THE APP
# -----------------------------------------------------------------------------
class biter(object):
    """
    bidirectional iterator
    """
    def __init__(self, collection=['one','two','three','four']):
        self.collection = collection
        self.index = -1

    def __next__(self):

        try:
            self.index += 1
            return self.collection[self.index]

        except IndexError:
            self.index = len(self.collection)
            raise StopIteration

    def prev(self):
        # prevent negative outcomes
        if self.index != 0:
            self.index -= 1

        return self.collection[self.index]



    def __iter__(self):
        return self


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
