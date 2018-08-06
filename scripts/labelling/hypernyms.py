# -- Imports ------------------------------------------------------------------

# base
import functools

# third party
import pandas as pd

# named
from nltk.corpus import wordnet as wn
from nltk import pos_tag


# -- Functions ----------------------------------------------------------------
class Hypernyms:
    """
    Part of the auto-generation of labels for clusters

    This class attempts to identify a suitable common hypernym for items
    within a cluster
    """

    def __init__(self, clusterconstructor, config):
        """
        Constructor for the Hypernyms object.
        Part of the labeling of clusters.
        This class is responsible for working through the labels
        and checking they have common hypernyms.

        Parameters
        ----------
        clusterconstructor : ClusterConstructor
            the cluster constructor object which contains data
            that will be labeled.
        config : dict
            a dictionary of configs

        Returns
        -------
        Hypernyms object

        """
        # init, called when class is instantiated

        self.clusters = clusterconstructor.clusters
        # the input wordlist
        self.stoppers = config['stoppers']

        # ---------------------------------------------------------------------

        # basic cleaning
        # noun cluster
        self.nouns = [[self.actors(s) for s in cluster]
                      for cluster in self.clusters]

        # ---------------------------------------------------------------------

        # intermediary objects so we can assess the classifier
        self.hypernyms = {c: self.hymns(self.nouns[i])
                          for i, cluster in enumerate(self.clusters)
                          for c in cluster}

        self.intersect = {c: self.common(cluster)
                          for cluster in self.clusters
                          for c in cluster}

        self.hierarchy = {c: self.distances(cluster)
                          for cluster in self.clusters
                          for c in cluster}

        # classification obtained
        self.label = {
            i: self.classification(c)
            for c in self.clusters for i in c}
        # remove those things which aren't classified
        # lower overhead than before

        # rewritten from self.classification(c) for performance testing
        # this version has a lookup rather than trying to run the function on
        # every cluster again and again
        self.accepted, self.rejected = self.accept(self.clusters)


        # tidying up the labels
        self.label = {i: j for i, j in self.label.items() if j}

    # --Functions -------------------------------------------------------------
    def hymns(self, cluster):
        """
        Find the hypernyms for the list of words

        Parameters
        ----------
        cluster : [str]
            a list of words to look for hypernyms

        Returns
        -------
        dict

        """
        nyms = {
            # only take the hypernyms which are nouns
            w: [s.hypernyms() for s in wn.synsets(w) if s.pos() == 'n']
            for w in cluster}

        # add the synset of the word itself
        for w in cluster:
            nyms[w].append(s for s in wn.synsets(w) if s.pos() == 'n')

        nyms = {
            group:
            [w for word in words for w in word if word != []]
            for group, words in nyms.items()}

        return nyms

    def common(self, cluster):
        """
        Find the common hypernyms for the list of words

        Parameters
        ----------
        cluster : [str]
            a list of words to look for common hypernyms

        Returns
        -------
        dict
            a dictionary for a given group containing its hypernyms

        """
        nyms = self.hypernyms[cluster[0]]


        def t(synset):
            """
            Get the text description of the hypernym from the synset

            Helper function to save having to write the output often
            """
            return synset[0].name().split('.')[0]

        def d(synset):
            """
            Companion to textise, returns the distance to this word
            """
            return synset[1]

        # generate the wordnet hierarchy for each string in wl
        hier = {
            key: [word.hypernym_distances() for word in value]
            for key, value in nyms.items()
        }

        # and then just tidy it up and bit and take the set of them
        hier = {
            key: {word for words in value for word in words}
            for key, value in hier.items()
        }

        # our aim now is to find the common items in all these sets
        # to do so we don't care whether it is food.n.01 or .02
        # and so we will strip that extra info off here
        groups = [{t(i) for i in group} for _, group in hier.items()]

        common_name = set.intersection(*groups)

        common = {
            key: [
                (t(word), d(word))
                for word in value if t(word) in common_name
            ]
            for key, value in hier.items()
        }

        # replacing the tuple with a dataframe
        common = {
            key: (
                pd.DataFrame(word, columns=('name', key))
                .groupby('name')
                .min()
                .reset_index()
            ) for key, word in common.items()
        }

        return common

    def distances(self, cluster):
        """
        Get a nice table of distances

        Parameters
        ----------
        cluster : [str]
            a list of words to look for common hypernyms

        """

        common = self.intersect[cluster[0]]

        combined = functools.reduce(
            lambda x, y: pd.merge(x, y, on='name'), common.values())
        combined['__all'] = combined.sum(numeric_only=True, axis=1)

        return combined

    def classification(self, cluster):
        """
        Get's the classification based on the shortest cumulative distance in
        the dataframe

        Parameters
        ----------
        cluster : [str]
            a list of words to look for common hypernyms

        """
        df = self.hierarchy[cluster[0]]

        if df.shape[0] > 0:
            shortest = df['__all'].min()
            labels = df[df['__all'] == shortest].name.tolist()
            labels = [i.replace("_", " ") for i in labels]
            return labels[0]
            
        else:
            return None

    def accept(self, clusters):
        """
        Decide whether a cluster is accepted for all clusters
        """

        for key, value in self.label.items():
            for cluster in clusters:
                for c in cluster:
                    for s in self.stoppers:
                        if self.label[key] == s:
                            self.label[key] = None

        accepted = [[bool(self.label[c]) for c in cluster]
                    for cluster in clusters]

        return ([c for c, a in zip(clusters, accepted) if a],
                [c for c, a in zip(clusters, accepted) if not a])

    def actors(self, string):
        """
        Extract the most suitable noun from a string
        """
        tags = pos_tag(string.split())
        nouns = [word[0] for word in tags if 'NN' in word[1]]

        try:
            return nouns[-1]
        except:
            return ''


# -- Boilerplate --------------------------------------------------------------
if __name__ == '__main__':
    print("Not to be used as a standalone program")
    raise
