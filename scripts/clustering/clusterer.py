# -- Imports ------------------------------------------------------------------

# third party
import pandas as pd
import scipy.cluster.hierarchy as H


# -- Definitions --------------------------------------------------------------
class Clusterer:
    """
    A class that embedds and clusters the strings.
    """

    def __init__(self, loader, model, config):
        """
        Constructor for the clusterer object.
        The main purpose of this is to load and process the data.

        Parameters
        ----------
        loader : Loader object
            a loader object containing formatted and preloaded data

        config : dict
            a dictionary of configs

        model : fastText model
            a loaded model from the fastText library
            required fro the embedding of the text

        Returns
        -------
        Clusterer object

        """

        # objects

        self.config = config
        self.model = model

        try:
            self.words = loader.words
            self.linked = loader.linked
        except:
            raise Exception("Not text descriptions loaded")

        self.vectors = self.embed(loader, model)
        self.Z = self.link()
        self.counts = self.count()

    # -- Functions ------------------------------------------------------------
    def count(self):
        """
        Count the unique strings

        Returns
        -------
        dict
            of the form {word:count}

        """
        freq = {}

        for desc in self.words:
            if desc in freq:
                freq[desc] += 1
            else:
                freq[desc] = 1

        return freq

    def embed(self, loader, model):
        """
        Embedd the words into the vector space using the given model

        Parameters
        ----------
        loader : Loader object
            a loader object containing formatted and preloaded data

        model : fastText model
            a loaded model from the fastText library
            required fro the embedding of the text

        Returns
        -------
        Clusterer object

        """
        print("    ** Embedding words")

        words = loader.words
        vectors = [model.get_word_vector(word) for word in words]

        return [(w, *v) for w, v in zip(words, vectors)]

    def link(self):
        """
        Perform ward linkage

        Returns
        -------
        pd.DataFrame of sequential ward linked nodes, distance and count of leave
        within the corresponding cluster

        """
        print("    ** Performing linkage")
        df = pd.DataFrame(self.vectors)
        Z = H.linkage(df.iloc[:, 2:], 'ward')
        Z = pd.DataFrame(Z, columns=('node1', 'node2', 'distance', 'count'))

        return Z


# -- Boilerplate --------------------------------------------------------------
if __name__ == '__main__':
    print("Not to be used as a standalone program, see main.py")
    raise
