# -- Imports ------------------------------------------------------------------

# base
import re

# third party
import pandas as pd


# -- Definitions --------------------------------------------------------------
class SimpleLoader:
    """
    A simplified version of the Loader class responsible for picking
    up the data after one depth iteration.
    """

    def __init__(self, words, linked):
        self.words = words
        self.linked = linked
        print('_'*79)
        print(f"    ** Reloaded {len(self.words)} items")


# -- Boilerplate -
class Loader:
    """
    A loading class for the data.
    """

    def __init__(self, config, data=None):
        """
        Constructor for the loading object.
        The main purpose of this is to load and process the data.

        Parameters
        ----------
        config : dict
            a dictionary of configs

        data : pandas.core.series.Series
            a series of strings which will be loaded and
            processed instead of the default dataset set in the
            config files
            (default=None)

        Returns
        -------
        Loader object

        """
        # objects
        self.config = config

        if data:
            if all([len(sublist) == 0 for sublist in data]):
                raise ValueError('Sublists in the given data are empty')
            self.words, self.linked = self.clean(data)
        else:
            self.words, self.linked = self.clean(self.load())

        # export the original desc
        pd.DataFrame(self.words).to_csv(
            'output/join_output.csv', header=False, index=False)

    # -- Functions ------------------------------------------------------------
    def load(self):
        """
        Load the data using pandas

        Returns
        -------
        pandas.core.frame.DataFrame
            a pandas dataframe object in the right shape for further processing

        """

        # setup
        descs = (pd
                 .read_csv(
                     self.config['data'],
                     header=None,
                     names=('description',))
                 .values
                 .tolist())

        return descs

    def clean(self, wl):
        """
        Pre-prepare the word lists, dealing with some common prepositions

        Parameters
        ----------
        wl : [[str]]
            a list of lists of strings to clean

        Returns
        -------
        list

        """

        # capture invalid lists
        if len(wl) == 0:
            raise ValueError('The list of words passed to self.clean is empty')
        elif not all([len(sublist) > 0 for sublist in wl]):
            raise ValueError('One or more of the sublists is empty')
        # elif not all([len(s) > 0 for sublist in wl for s in sublist]):
        #     raise ValueError('One or more strings in your list are empty')

        def __go(word):
            """
            Processing of each of the single descriptions
            """
            w = str(word[0]).lower()

            for regex, replacement in self.config['regex']:
                w = re.sub(regex, replacement, w)

            for key, value in self.config['trouble'].items():
                w = re.sub(key, value, w)

            if len(w) == 0:  # this ensures that a string is still returned
                w = ''

            return w

        lookup = {}
        words = []
        for word in wl:
            clean_word = __go(word)
            lookup[word[0]] = clean_word
            words.append(clean_word)

        words = [word for word in words if word]  # discard empty strings

        print(f"    ** Loaded {len(words)} items")
        return list(set(words)), lookup


# -- Boilerplate --------------------------------------------------------------
if __name__ == '__main__':
    print("Not to be used as a standalone program, see main.py")
    raise
