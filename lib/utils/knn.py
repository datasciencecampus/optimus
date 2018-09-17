# -- Imports ------------------------------------------------------------------

# base
import time

# third party
from sklearn.neighbors import KNeighborsClassifier
import numpy as np
import pandas as pd

# named


# -- Functions ----------------------------------------------------------------
class KNN:
    """
    Part of the Optimus pipeline

    Main purpose is to pick up unlabeled entries and apply a KNN classifier
    trained on all the labeled data. This will then assign the tier_n (n is the
    last itteration of Optimus) based labels to the unlabeled data based on
    spacial proximity.

    """

    def __init__(self, gatekeeper, matrix):
        """
        Constructor for the KNN operator

        Parameters
        ----------
        gatekeeper : Gatekeeper object
            the gatekeeper object after all iterations have been completed
            in the optimus pipeline

        matrix : fastText model object
            a fast text model required to reembedd the leftover non_selected
            string
        Returns
        -------
        KNN object

        """

        # need it for the __call__ to be able to access the model
        self.matrix = matrix
        # save gatekeeper into an attribute
        self.gatekeeper = gatekeeper

        #only keep duplicates to train knn - implicitly these have and are exclusively
        # those that have been relabelled
        df = gatekeeper.prowl
        ids = df["current_labels"]

        print(f"ids")
        print(ids)

        self.train_data= df[ids.isin(ids[ids.duplicated()])]

        self.train_knn = np.array(
            self.embed(self.train_data["current_labels"], self.matrix)
        )

        print(f"self.train_knn")
        print(self.train_knn)

        # TODO: check if the Gatekeeper.non_selected is really what we need to
        self.non_selected = np.array(
            self.embed(gatekeeper.non_selected, self.matrix))
        # extract the current_labels from the prowl object in hottrod
        # TODO: make sure the code here takes the right labels to be
        # trained upon.
        self.current_labels = np.array(self.embed(
            gatekeeper.prowl['current_labels'].values.tolist(), self.matrix))
        # pretty obvious, but - fit the sklearn KNN
        self.fitKNN()

    def embed(self, words, model):
        """
        Perform the embedding of the non_selected words

        # TODO: Very similar to what is available in the clusterer class
                possible to remove duplication of functions.

        Parameters
        ----------
        words : list
            a list containing the words to be embedded

        model : fastText model object
            a model to use when embedding the words

        Returns
        -------
        list
            a list of tuples with words and vectors

        """
        # use the fast text model to perform embeddings
        vectors = [model.get_word_vector(word) for word in words]

        return [(w, *v) for w, v in zip(words, vectors)]

    def fitKNN(self):
        """
        Fit a KNN classifier on the current_labels attribute of
        wheeljack. Currently uses the default parameters for the
        sklearn KNeighborsClassifier class. Could be made more flexible

        Runs as part of the constructor

        Returns
        -------
        None

        """
        # create an fit a classifier based on the current_labels data
        classifier = KNeighborsClassifier(n_neighbors=2)
        train_X = self.train_knn[:, 1:]
        train_y = self.train_knn[:, 0]

        print(train_y)

        classifier.fit(train_X, train_y)
        self.KNN = classifier

    def __call__(self, X=None):
        """
        Predict the labels for either the non_selected attribute
        from the Gatekeeper object (see constructor) or the given X.

        Parameters
        ----------
        X : list
            a list of string to run the predictions on.

            Note:
            -----
            The KNN is still trained on the accepted data.

        Returns
        -------
        numpy.array
            an array of original words and their predicted labels
            based on the accepted words that the KNN was trained on

        """
        # run the newly passed labels through the embedding etc and
        # get predictions for them
        if X:
            print("or this one")
            predictions = self.KNN.predict(
                np.array(self.embed(X, self.matrix))[:, 1:])
            return np.array(list(zip(X, predictions)))
        else:  # if no X is passed run the non_selected labels from gatekeeper
            print("correct prediction triggered")
            pred =  np.array(
                list(
                    zip(
                        self.non_selected,
                        self.KNN.predict(self.current_labels[:, 1:])
                    )
                ))
            print("current_labels")
            print(self.current_labels[:, 1:])
            print(self.current_labels[:, 1:].shape)
            print(f"pred")
            print(pred)
            return(pred)

    def __slideshow(self):
        """
        Produce a feed of randomly selected entries from the
        non_selected label with both their ORIGINAL label and a
        label predicted by the KNN classifier. This is mainly to
        showcase the predictions for inspection.

        NOTE: This works on an infinite loop basis so if you start it
        you'll have to send an interrupt command to the kernel.
        """
        while True:
            print('\nNOTE: Interrupt kernel to stop the slideshow')
            selection = self.non_selected[np.random.randint(
                0, len(self.non_selected)), :]
            print(f'Original Label: {selection[0]}\n',
                  f'Prediction: {self.KNN.predict(selection[1:].reshape(1,-1))[0]}')
            time.sleep(3)


# -- Boilerplate --------------------------------------------------------------
if __name__ == '__main__':
    print("Not to be used as a standalone program")
    raise
