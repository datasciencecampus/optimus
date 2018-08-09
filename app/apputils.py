# imports
# third party
import pandas as pd
import dash

# NON-CALLBACK FUNCTIONS REQUIRED FOR THE APP
# -----------------------------------------------------------------------------
def unique_gen(lst):
    """
    Creates a generator that will alow to
    use the 'next' function to move through.all
    clusters.
    """
    for item in lst:
        yield item

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
