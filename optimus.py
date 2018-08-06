# -- Imports ------------------------------------------------------------------
# base
import json
import gc

# third party
import fastText as ft
import pandas as pd

# project
from scripts.data import Loader
from scripts.clustering import Clusterer, ClusterConstructor
from scripts.labelling import EditDistance, WordGram, CharGram, Hypernyms
from scripts.utils import Gatekeeper, KNN


# -- Load Configs -------------------------------------------------------------
class Optimus:

    def __init__(self, config_path='', **kw):
        """
        Constructor for the Optimus pipeline object

        This initialised the main access point to the Optimus pipeline.

        Note:
        -----
        The constructor accepts keyword arguments that will overwrite the
        default settings of Optimus. For example distance=2 will overwrite the
        distance parameter for the object.

            Example
            ----------
            o = Optimus(config_path='here/lies/my/config.json',
                        distance = 2,
                        cutoff = 10,
                        stepsize = 3,
                        ...
                        )

        Parameters
        ----------
        config_path : str
            a path to a custom config file created by the user. It has to be a
            a .json file following the structure of the default config.json
            file found in the etc folder

        Returns
        -------
        Optimus object

        """

        self.kw = kw
        self.config_path = config_path

    def load_config(self, path='', default_config='./etc/config.json'):
        """
        Load the provided config file into memory and assign it to the
        Optimus object as the config attribute.

        If no path is provided upon construction of the Optimus object,
        this method will default to the './etc/config.json' file for the
        settings. It will also pick up any keyword arguments passed to the
        __init__ function.

        Parameters
        ----------
        path : str
            a path string to the config file. under normal circumstances this
            will be picked up from the __init__ function

        default_config : str
            a default config path to use for base configs.
            (default='./etc/config.json')

        Returns
        -------
        dict
            a config dictionary containing all the required configurations
            for the rest of the pipeline

        """

        # load the default configs
        try:
            config = json.load(open(default_config))
        except FileNotFoundError:
            raise FileNotFoundError(
                f'Default configs failed to load from {default_config}')

        # update config with user config from file
        if path:
            try:
                user_config = json.load(open(path))
            except FileNotFoundError:
                print(
                    '-- WARNING: User config file failed to load.\n',
                    '-- WARNING: Please check location provided')
            else:
                for key, value in user_config.items():
                    config[key] = value
        else:
            self.vprint("-- Custom user config were not found.")
            self.vprint("-- Using defaults as base configs.")

        # update config with user configs from kwargs
        if self.kw:
            self.vprint('-- Following valid configs were passed manually:')
            for key, value in self.kw.items():
                if key in config.keys():
                    self.vprint(f'    - {key}: {value}')
                    config[key] = value

        return config

    def catch_input(self, input):
        """
        Catch the input provided by the user and ensure it is a pandas
        Series object. If this is the case then reformat it into a list
        of form [[str]]

        Parameters
        ----------
        input : pandas.core.series.Series
            the input column that the function will check and transform

        Returns
        -------
        list
            a list of the form [[str]]

        """
        # check if the type is correct
        if type(input) == pd.core.series.Series:
            return [[str(w)] for w in input]  # process it into the right shape
        else:
            if hasattr(input, "__iter__"):  # check if input is iterable
                raise ValueError(
                    'Non pandas Series iterables are not supported')
            else:
                return None

    def handle_output(self, prowl, save_csv=False, full=False, out_col=-1):
        """
        The function that handles how the output of the pipeline is presented
        to the user.

        If the user does not set the full parameter to True, only the last
        column from prowl will be returned.

        Parameters
        ----------
        prowl : pandas.core.frame.DataFrame
            a pandas dataframe that is constructed during the runing of the
            pipeline

        save_csv : bool
            if true will save the full prowl to a csv file
            (default=False)

        full : bool
            if true will return the whole of prowl to the user, otherwise only
            the last column of prowl (the last depth iteration results) will be
            returned to the user
            (default=False)

        Returns
        -------
        pd.core.series.Series / pd.core.frame.DataFrame
            full or partial results of the pipeline

        """
        if save_csv:
            prowl.to_csv('optimus_results.csv', header=True, index=False)

        if full:
            return prowl

        else:
            return prowl.iloc[:, out_col]

    def vprint(self, string):
        """
        A very simple function which will either print or not depending on the
        verbosity setting of the Optimus object

        Parameters
        ----------
        string : str
            a string to print if self.verbose == True

        Returns
        -------
        None

        """
        if self.verbose:
            print(string)

    def __call__(self,
                 data=None,
                 save_csv=False,
                 full=False,
                 verbose=True,
                 runKNN=False):
        """
        By calling this function the user will start the processing of the
        pipeline.

        If no data is provided to this function under the data parameter it
        will take the path provided in the config['data'] entry, load it
        and use it. It is useful as a fallback option, however it is expected
        that as part of the integration of Optimus into a pipeline, some
        data will be passed to this function call.

        Parameters
        ----------
        data : pd.core.series.Series
            a series object containing the strings that need to be processed
            (default=None)

        save_csv : bool
            this dictates if the full prowl will be saved as a csv
            (default=False)

        full : bool
            this dictates if the data returned to the user in the form of a
            full dataframe or just a series of predicted labels
            (default=False)

        verbose : bool
            this parameter dictates how much will be printed. if false only a
            few lines will be output.
            (default=True)

        runKNN : bool
            this parameter dictates if the K Nearest Neighbour algorythm will
            be applied to the labels that are not picked up in the normal run
            of optimus

        Returns
        -------
        pd.core.series.Series / pd.core.frame.DataFrame
            depending on the full setting this will return the output of the
            last depth or a full dataframe with outputs from each iteration

        """
        # set the verbosity setting
        self.verbose = verbose

        # notes
        self.vprint('-- Performing setup')
        self.vprint('_' * 79)

        # load config before each run
        self.config = self.load_config(self.config_path)

        # reformat provided series into accepted format
        data = self.catch_input(data)

        # build looping mechanism, adding 1 to the depth of
        # ratchet and changing the dataset passing through the classes

        # free text loading
        self.vprint("-- Loading descriptions")
        if data:
            self.vprint("-- Ingesting provided series")
            L = Loader(self.config, data)
        else:
            self.vprint("-- No custom data provided, using data from config")
            L = Loader(self.config)

        # start a dataframe that will track the labels at each level
        prowl = pd.DataFrame.from_dict(L.linked, orient='index')
        prowl = prowl.reset_index()
        prowl.columns = ['original', 'current_labels']

        # embed the words using fastText
        if hasattr(self, "matrix"):
            self.vprint("-- Model already loaded")

        else:
            self.vprint("-- Loading model")
            self.matrix = ft.load_model(self.config['model'])

        self.vprint("-- Embedding")
        clusterer = Clusterer(L, self.matrix, self.config)

        # clustering
        self.vprint("-- Clustering")
        CC = ClusterConstructor(clusterer, self.config)

        # start the loop for each depth
        self.vprint('_' * 79)  # some decoration
        while CC.iterate:

            self.vprint(f"-- Depth: {CC.distance}")  # some decoration
            self.vprint('_' * 79)  # some decoration

            # edit distance based metrics
            ED = EditDistance(CC, self.config)
            # push the rejected clusters back to the ClusterConstructor
            # for the next phase
            CC.clusters = ED.rejected
            self.vprint(
                f"    ** | Edit Distance   | classified: {len(ED.accepted)}")

            # class for character and word n-gram and scoring
            WG = WordGram(CC, self.config)
            # push the rejected clusters back to CC for the next phase
            CC.clusters = WG.rejected
            self.vprint(
                f"    ** | Word Grams      | classified: {len(WG.accepted)}")

            # class for character and word n-gram and scoring
            CG = CharGram(CC, self.config)
            # push the rejected clusters back to CC for the next phase
            CC.clusters = CG.rejected
            self.vprint(
                f"    ** | Character Grams | classified: {len(CG.accepted)}")

            # class for finding suitable hypernyms from WordNet
            HN = Hypernyms(CC, self.config)
            # push the rejected clusters back to CC for the next phase
            CC.clusters = HN.rejected
            self.vprint(
                f"    ** | Hyponyms        | classified: {len(HN.accepted)}")

            # gatekeeper, overwrites the CC with what it needs for the
            # next push
            H = Gatekeeper(CC, ED, WG, CG, HN, self.matrix, self.config, prowl)

            CC = H.clusterconstructor
            prowl = H.prowl

            self.vprint('_' * 79)

        # if requested run a KNN on the non_labeled data
        if runKNN:
            self.vprint(f"-- Performing KNN")
            K = KNN(H, self.matrix)
            self.KNN_predictions = pd.DataFrame(K())
            self.KNN_predictions.to_csv('output/knn.csv')

        # clean up after yourself
        self.clean_up()

        # return output
        return self.handle_output(prowl, save_csv=save_csv, full=full)

    def clean_up(self):
        """
        A quick function to call the garbage collector to remove the loaded
        model from memory.

        """
        del(self.matrix)
        gc.collect()

    def replace_model(self, model=None):
        """
        This function allows the user to replace existing model that is loaded
        in memory during the first run call of a given Optimus project with
        another fast text model.

        If no model is loaded (meaning that Optimus has not been called yet)
        it will load a given model into the Optimus object.

        If a model was loaded prior and no model is passed to replace it, it
        will be deleted and garbage collected.

        Parameters
        ----------
        model : str / fastText model object
            this will be the model that is (loaded and) passed onto the Optimus
            object

        Returns
        -------
        None

        """
        # catch any incorrectly passed models
        model_type = type(model)

        if model_type not in [ft.FastText._FastText, model_type]:
            raise ValueError(
                'Model can only be a fastText model or string path'
            )
        elif model_type == str:
            print(f'-- Loading model from given path {model}')
            try:
                model = ft.load_model(model)

            except ValueError:
                raise ValueError('The given path could not be loaded.')

        elif model_type == ft.FastText._FastText:
            print('-- A loaded model is provided.')

        if model:
            if hasattr(self, 'matrix'):
                print('-- Cleaning up old model before reassigning')
                self.clean_up()

            print('-- Assigning the given model the Optimus object')
            self.matrix = model

        else:
            print('-- No model provided. Cleaning up the loaded model')
            self.clean_up()


# -- Boilerplate --------------------------------------------------------------
if __name__ == '__main__':
    print('Not to be run as a standalone package for now.')
