# -- Imports ------------------------------------------------------------------

# base
import itertools
import math

# third party
import pandas as pd

from nltk.tokenize import word_tokenize


# -- Definitions --------------------------------------------------------------
class WordGram:
    """
    Part of the auto-generation of labels for clusters.

    This function looks for sufficiently frequent and lengthy
    sequential combinations of words within cluster items.
     
    """

    def __init__(self, clusterconstructor, config):
        """
        Constructor for the WordGram object.
        Part of the labeling of clusters.
        This class is responsible for finding the most common word in the
        clustered labels for each cluster.

        Parameters
        ----------
        clusterconstructor : ClusterConstructor
            the cluster constructor object which contains data
            that will be labeled.
        config : dict
            a dictionary of configs

        Returns
        -------
        WordGram object

        """

        # objects
        self.threshold = config['wg_threshold']
        self.clusters = clusterconstructor.clusters

        self.w_grams,\
            self.w_counts,\
            self.wg_all_scores,\
            self.wg_labels,\
            self.accepted,\
            self.rejected = self.words()

        self.label = {
            i: key
            for key, value in self.wg_labels.items()
            for i in value
        }

    def word_grams(self, words):
        """
        Generate a list of ngrams for each word in the list.

        Parameters
        ----------
        words : list
            a list of words to generate ngrams from

        Returns
        -------
        list
            ngram list

        """
        ngram_list = [
            w
            for w in itertools.chain.from_iterable(
                itertools.combinations(words, i)
                for i in range(1, len(words) + 1))
        ]

        return ngram_list

    def words(self):
        # lists to collect cluster word-gram combinations
        all_ngram = []
        # list to collect dictionaries of word gram counts for each cluster
        wg_counts = []

        accepted = []
        rejected = []

        # we test to make sure that there is at least one word with length long
        # three characters - this flag is used to only append if that tis the c
        flag_include = True

        all_scores = []
        links = {}
        for cluster in self.clusters:
            # list to collec tthe cluster word grams
            ngram = []
            # dictionary to count the occurance of tuples within the cluster
            counts = {}

            for item in cluster:
                # tokenise the string in a cluster
                words = word_tokenize(item)

                # skip empty lists
                if not words:
                    flag_include = False
                else:
                    # test for length of word greater than three
                    max_word_length = max([len(i) for i in words])

                    if max_word_length < 3:
                        flag_include = False
                    else:
                        flag_include = True
                        # get word grams for the tokenised word list
                        wg = self.word_grams(words)
                        # convert word grams to tuples
                        wg = [tuple(item) for item in wg]
                        # append word gram tuples to cluster list
                        ngram.append(wg)

            # once all items in a cluster have had word grams established
            # for each set of word grams

            if flag_include:
                for item in ngram:
                    # for each individual wordgram add it to the dictionary
                    for i in item:
                        if i in counts:
                            counts[i] += 1
                        else:
                            counts[i] = 1

                all_ngram.append(ngram)
                wg_counts.append(counts)
                df_wordgrams = pd.DataFrame([[n, counts[n]] for n in counts])
                df_wordgrams.columns = ["wordgram", "no"]

                df_wordgrams['length'] = df_wordgrams.apply(
                    lambda row: len(row.wordgram), axis=1)

                df_wordgrams['score'] = df_wordgrams.apply(
                    lambda row: row.no * row.no * (1 + math.log(row.length)),
                    axis=1)

                df_wordgrams = df_wordgrams.sort_values(
                    "score",
                    ascending=False)

                all_scores.append(df_wordgrams)

                new_label = " ".join([str(x) for x in df_wordgrams.iloc[0][0]])

                if df_wordgrams.iloc[0, 3] / len(cluster) > self.threshold:
                    accepted.append(cluster)
                    links[new_label] = cluster
                else:
                    rejected.append(cluster)
            else:
                rejected.append(cluster)

        return all_ngram, wg_counts, all_scores, links, accepted, rejected


# -- Boilerplate --------------------------------------------------------------
if __name__ == '__main__':
    print("Not to be used as a standalone program")
    raise
