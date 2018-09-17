# -- Imports ------------------------------------------------------------------

# base
import numpy as np


# -- Definitions --------------------------------------------------------------
class ClusterConstructor:
    """
    An object which uses the Loader class and its attributes to structure
    and format the clustering outputs.
    """

    def __init__(self, clusterer, config, previous=None):
        """
        Constructor for the ClusterConstructor object.
        This uses the Loader class and its attributes to structure
        and format the clustering outputs.

        Parameters
        ----------
        clusterer : Clusterer object
            this takes in a Clusterer object instance which has performed
            string clustering

        config : dict
            a dictionary of configs

        Returns
        -------
        ClusterConstructor object

        """

        # objects
        self.config = config

        self.distance = config['distance']

        # create pointers to the data from clusterer
        self.words = clusterer.words
        self.vectors = clusterer.vectors
        self.Z = clusterer.Z

        self.clusters = self.form_clusters()
        selected = [word for cluster in self.clusters for word in cluster]
        self.non_selected = [
            word for word in self.words if word not in selected]

        # this will be overwritten further down the line by gatekeeper
        # and will decide when to stop doing the work
        self.iterate = True

        # holds the output from the last iteration, used by gatekeepr to decide
        # whether or not to continue the iterations
        self.previous = previous

        print(f"    ** Generated {len(self.clusters)} clusters")

    def form_clusters(self):
        """
        The key method for the cluster constructor.
        It takes in the Z attribute produced during the clustering stage of
        Clusterer and extracts the appropriate heirachy and clusters.

        Returns
        -------
        list

        """
        def retrieve_clusters(Z, leaves, labels):
            """
            given the ward-linked array, a list of leaf indices and the label
            list returns a list of the words in a cluster

            @params
                Z  =  [[Rational]]
                leaves = [Int]
                labels = [Int]
            """
            while np.max(leaves) > Z.shape[0]:
                m = np.max(leaves)
                leaf = int(m) - len(labels)
                # so the above can send us on an infinite loop if the occasion
                # just so
                # happens to be right, let's not let negative leaf values exist
                if leaf > 1:
                    leaves += [Z.iloc[leaf, 0], Z.iloc[leaf, 1]]
                leaves.remove(m)

            leaves = [int(leaf) for leaf in leaves]
            words = [labels[leaf] for leaf in leaves]

            return words

        # list to collect our clusters
        word_list = []
        # list of non selected clusters based on distance criterion
        non_selected = []

        # iterate through linkage data frame and create clusters
        for i, row in self.Z.iterrows():
            item = []
            ns_item = []
            # if the leaves satisfy our distance threshold then
            if row[2] < self.distance:
                leaves = [row[0], row[1]]
                item.append(retrieve_clusters(self.Z, leaves, self.words))
                word_list += item
            else:
                leaves = [row[0], row[1]]
                ns_item.append(retrieve_clusters(self.Z, leaves, self.words))
                non_selected += ns_item
        # Now we walk backwards through the list throwing away anything we've
        # already encountered
        # The justification for this is that it is a sequential process linking
        # closely formed clusters together - by starting at the end and stepping
        # back through the clusters we can ignore any subclusters that formed
        # larger clusters toward the end of the process.
        # As this functionality is needed for both the selected and non selected
        # clusters it was wrapped in a function

        def strip(ls):
            stripped = []

            for group in ls[::-1]:
                flat = []
                for item in group:
                    flat.append(item)

                exclude = np.sum(set(flat) <= set(added) for added in stripped)
                if not exclude:
                    stripped.append(flat)

            return stripped

        self.non_selected = [w for l in strip(non_selected) for w in l]

        return strip(word_list)


# -- Boilerplate --------------------------------------------------------------
if __name__ == '__main__':
    print("Not to be used as a standalone program")
    raise
