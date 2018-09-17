# -- Imports ------------------------------------------------------------------

# third party
import pandas as pd
import numpy as np

# project
from lib.data import SimpleLoader
from lib.clustering import Clusterer, ClusterConstructor

# -- Definitions --------------------------------------------------------------


class Gatekeeper:
    """
    An object that collects the outputs from the labelers and
    guides the end of an Optimus loop to the next iteration.
    """

    def __init__(self,
                 clusterconstructor,
                 editdist,
                 wordgram,
                 chargram,
                 hypernyms,
                 matrix,
                 config,
                 prowl):
        """
        Constructor for the Gatekeeper object.

        Parameters
        ----------
        clusterconstructor : ClusterConstructor
            a ClusterConstructor object required to pull
            the data together and to continue the pipeline

        edidist : EditDistance
            the EditDistance object that was part of the pipeline.
            Its resulting labels will be collected by the gatekeeper.

        wordgram : WordGram
            the WordGram object that was part of the pipeline.
            Its resulting labels will be collected by the gatekeeper.

        chargram : CharGram
            the CharGram object that was part of the pipeline.
            Its resulting labels will be collected by the gatekeeper.

        hypernyms : Hypernyms
            the Hypernyms object that was part of the pipeline.
            Its resulting labels will be collected by the gatekeeper.

        matrix : fastText model object
            a model that will be used to embedd words into vectors

        config : dict
            a dictionary that contains settings for the whole pipeline

        prowl : pandas.core.frame.Frame
            a pandas dataframe which contains the labels from previous
            iterations alongside the original labels

        Returns
        -------
        Gatekeeper object

        """

        # pass config as a class attribute.
        self.config = config

        config['distance'] += config['stepsize']
        config['tier_counter'] += 1

        # list of strings that were not selected upon initial threshold filter
        self.non_selected = clusterconstructor.non_selected

        linked = {}

        # join the original to the accepted
        self.accepted = self.collect_accepted(
            editdist, wordgram, chargram, hypernyms)

        # combine all of the generated labels

        if self.accepted.shape:

            self.accepted.columns = ['from', 'to']

            self.prowl = pd.merge(prowl,
                                  self.accepted,
                                  left_on="current_labels",
                                  right_on='from',
                                  how='left')

            self.prowl.loc[:, 'to'] = np.where(
                self.prowl.loc[:, 'to'].isnull() == True,
                self.prowl.loc[:, 'current_labels'],
                self.prowl.loc[:, 'to'])

            self.prowl = (self.prowl
                          .rename(
                              columns={
                                  "current_labels":
                                  f"tier_{config['tier_counter']}",
                                  "to":
                                  "current_labels"
                              })
                          .drop(['from'], axis=1))
        else:
            pass

        words = list(set(self.prowl['current_labels'].tolist()))

        if clusterconstructor.distance == config['cutoff']:
            self.clusterconstructor = self.Iter_switch()
        else:
            simpleloader = SimpleLoader(words, linked)
            clusterer = Clusterer(simpleloader, matrix, config)
            self.clusterconstructor = (ClusterConstructor(
                clusterer,
                config,
                previous=clusterconstructor.words))

    # stripped down ClusterConstructor to enable iterations to complete
    # TODO: eventually this needs to be extracted from here
    class Iter_switch:
        def __init__(self):
            self.iterate = False

    def concat(self, *args):
        """
        Take the labels from each labeling object and put them in the required
        format.

        """

        labels = []
        descriptions = []

        for arg in args:
            for desc, label in arg.label.items():
                if isinstance(label, str):
                    labels.append(label)
                    descriptions.append(desc)
                elif isinstance(label, list):
                    for i in range(len(desc)):
                        labels.append(label)
                        descriptions.append(desc[i])

        df = pd.DataFrame({'description': descriptions, 'label': labels})
        return df

    def collect_accepted(self, *args):
        """
        Collect all the accepted string labels from the given labeling objects

        Parameters
        ----------
        args : labeling objects (EditDistance, WordGram etc.)
            the objects that have ran through the cluster names in the latest
            iteration

        Returns
        -------
        pandas.core.frame.DataFrame
            pandas dataframe with the original word and the proposed labels

        """
        accepted = [flat for i in args for flat in i.label.items()]

        if len(accepted):
            return pd.DataFrame(accepted)
        else:
            return pd.DataFrame({'from': [], 'to': []})


# -- Boilerplate --------------------------------------------------------------
if __name__ == '__main__':
    print("Not to be used as a standalone program")
    raise
