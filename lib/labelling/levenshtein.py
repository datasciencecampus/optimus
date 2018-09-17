# -- Imports ------------------------------------------------------------------

# base
import itertools

# third party
import numpy as np

from nltk.metrics.distance import edit_distance


# -- Definitions --------------------------------------------------------------
class EditDistance:
    """
    Part of the auto-generation of labels for clusters.

    This class is responsible for working through the labels in a cluster
    and finding the average pair-wise levenshtein distance.

    If the average pair-wise lavenshtein distance satisfies a threshold
    then a cluster is relabelled with an appropriate label
    """

    def __init__(self, clusterconstructor, config):
        """
        Constructor for the EditDistance object.

        Parameters
        ----------
        clusterconstructor : ClusterConstructor
            the cluster constructor object which contains data
            that will be labeled.
        config : dict
            a dictionary of configs

        Returns
        -------
        EditDistance object

        """
        self.threshold = config['lev_threshold']
        self.clusters = clusterconstructor.clusters

        # find those clusters for which the label is suitable
        self.accepted = [
            c for c in self.clusters if self.lad(c) <= self.threshold]
        self.rejected = [c for c in self.clusters if c not in self.accepted]

        # for those clusters we do apply this to, generate the label to apply
        self.label = {
            i: self.common(item)
            for item in self.accepted
            for i in item
        }

    def ald(self, a, b):
        """
        Average list distance

        Parameters
        ----------
        a : [str]
            comparison list
        b : [str]
            comparison list

        Returns
        -------
        num

        """
        p = itertools.product(a, b)

        dists = [[edit_distance(i, j, transpositions=True)
                  for j in b] for i in a]
        avgs = [np.mean(dist) for dist in dists]

        return np.mean(avgs)

    def common(self, a):
        """
        Find the most common element of a list

        Parameters
        ----------
        a : [str]
            list of strings to work on

        Returns
        -------
        num
        """
        return max(set(a), key=a.count)

    def lad(self, a):
        """
        List average distance between words

        Parameters
        ----------
        a : [str]
            list of strings to work on

        Returns
        -------
        num
        """
        if len(a) == 1:
            return 0
        else:
            dists = [edit_distance(i, j)
                     for i, j in itertools.combinations(a, 2)]
            return np.mean(dists)


# -- Boilerplate -----------------------------------------------------------------
if __name__ == '__main__':
    print("Not to be used as a standalone program")
    raise
