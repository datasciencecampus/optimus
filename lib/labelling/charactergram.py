# -- Imports ------------------------------------------------------------------

# base
import itertools
import math

# third party
import numpy as np
import pandas as pd

from nltk.metrics.distance import edit_distance


# -- Definitions --------------------------------------------------------------
class CharGram:
    """
    Part of the labeling of clusters.
    This class is responsible for working through the labels
    and checking they have common character n-grams
    """

    def __init__(self, clusterconstructor, config):
        """
        Constructor for the CharGram object.
        Part of the auto-generation of labels for clusters

        This class attempts to identify sufficiently long and frequent
        substrings of items within a cluster as potential labels.

        Parameters
        ----------
        clusterconstructor : ClusterConstructor
            the cluster constructor object which contains data
            that will be labeled.
        config : dict
            a dictionary of configs

        Returns
        -------
        CharGram object

        """

        # objects
        self.threshold = config['ng_threshold']
        self.clusters = clusterconstructor.clusters

        (self.n_grams,
         self.ng_all_scores,
         self.ng_lookup,
         self.accepted,
         self.rejected) = self.get_ngrams()

        self.label = self.ng_labels()

    def characters(self, wl, nstart=3, nend=20):
        """
        Find a list of all ngrams of the provided size

        Parameters
        ----------
        wl : [str]
            a list of strings to perform the operation on
        nstart : int
            shortest ngram
        nend : int
            length of the longest ngram to be considered

        Returns
        -------
        list

        """

        # left as-is because its far more readable like this
        all_ngrams = []
        ngram_list = []

        # for each word in the wordlist
        for word in wl:
            # for qualifying lengths of n grams construct a list of substrings
            # for a single item
            for n in range(nstart, nend):
                ngram_list.append([word[i:i + n]
                                   for i in range(len(word) - n + 1)])

        # consolidates n grams for all items in cluster into one list
        for line in ngram_list:
            for word in line:
                all_ngrams.append(word)

        return all_ngrams

    def count_ngrams(self, ngram_list):
        """
        For a list of character ngrams - returns table of scores.

        Parameters
        ----------
        ngram_list : [str]
            a list of strings to perform the operation on

        Returns
        -------
        pandas.core.frame.DataFrame
            score table

        """
        # lets count the occurance of a specific word gram across the cluster
        ngrams = {}
        for ngram in ngram_list:
            if ngram in ngrams:
                ngrams[ngram] += 1
            else:
                ngrams[ngram] = 1

        # create a data frame for a lcuster of items
        # ngram | count | length | score (count*length)
        ngram_count_list = pd.DataFrame([[n, ngrams[n]] for n in ngrams])
        ngram_count_list.columns = ["ngram", "no"]
        ngram_count_list['length'] = ngram_count_list.apply(
            lambda row: len(row.ngram), axis=1)
        ngram_count_list['score'] = ngram_count_list.apply(
            lambda row: row.no * row.no * (1 + math.log(row.length)), axis=1)
        ngram_count_list = ngram_count_list.sort_values(
            "score", ascending=False)

        return ngram_count_list

    def get_ngrams(self):
        """
        Scores each cluster and handles the output of qualifying ngram labels

        """

        ngrams = []
        ngram_measures = []
        links = {}
        items = []
        accepted = []
        rejected = []

        # for each cluster of items
        for cluster in self.clusters:
            # check that a cluster has at least 2 items - should always be the
            # case

            lv = self.lad(cluster)
            if len(cluster) < 2:
                items.append("NONE")
                ngrams.append("NONE")
                ngram_measures.append("NONE")
                # if cluster length <2 then dont propose a label
                links[tuple(cluster)] = ('None',)
                rejected.append(cluster)

            else:
                n = self.characters(cluster)
                # if there are no n-grams that qualify (3gram - 20gram in our
                # code above) then dont propose a label
                if not n:
                    links[tuple(cluster)] = ('None',)
                    rejected.append(cluster)
                else:
                    # process and propose an appropriate label for the cluster
                    items.append(cluster)
                    ngrams.append(n)

                    ngram_measures.append(self.count_ngrams(ngrams[-1]))

                    if ngram_measures[-1].iloc[0, 3] \
                       / (lv * math.log(len(cluster))) > self.threshold:
                        accepted.append(cluster)
                        links[tuple(cluster)] = ngram_measures[-1].iloc[0, 0]
                    else:
                        rejected.append(cluster)

        return ngrams, ngram_measures, links, accepted, rejected

    def ng_labels(self):
        """
        Function to return a processed label (not tuples)
        """

        labels = {
            i: value.strip()
            for key, value in self.ng_lookup.items()
            for i in key
        }

        return labels

    def lad(self, a):
        """
        List average distance between words

        Parameters
        ----------
        a : [str]
            words to compare

        """

        if len(a) == 1:
            return 0
        else:
            dists = [edit_distance(i, j)
                     for i, j in itertools.combinations(a, 2)]
            return np.mean(dists)


# -- Boilerplate --------------------------------------------------------------
if __name__ == '__main__':
    print("Not to be used as a standalone program")
    raise
