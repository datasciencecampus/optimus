import re
import fastText as ft
import pandas as pd
import json
from sklearn.manifold import TSNE
from bokeh.plotting import figure, save, output_file
from bokeh.models import ColumnDataSource, LabelSet



def default_cleaner(word):
    """
    The default clearner used to get the strings in shape.
    Uses the default config.json location which contains replacements
    (trouble words) and other parameters. This is closely based off
    the optimus pipeline

    Parameters
    ----------
    word : str
        a string description of some sorts

    Returns
    -------
    str
        a cleaned string

    """
    config = json.load(open('config.json'))

    w = str(word).lower()

    for regex, replacement in config['regex']:
        w = re.sub(regex, replacement, w)

    for key, value in config['trouble'].items():
        w = re.sub(key, value, w)
    return w


def embed_words(words, model, cleaner, output_path):
    """
    The function that embeds plots using the fastText model.

    Parameters
    ----------
    words : iter
        some form of iterable containing strings
    model : str | fastText.model
        a string to the model or a fastText model
    cleaner : func
        a function to use to clean the strings.
        It should take in: word :: str -> str
    output_path : str
        if provided, this path will dictate where
        the embedded vectors will be saved (useful if
        the embeddings is all that is needed)

    Returns
    -------
    pandas.core.frame.DataFrame
        a pandas dataframe with the strings and
        the 300 dimensional vectors for each sized
        n x 300

    """

    if type(model) == str:
        model = ft.load_model(model)

    vectors = [model.get_word_vector(cleaner(word)) for word in words]
    output = pd.DataFrame([(w, *v) for w, v in zip(words, vectors)])

    if output_path:
        output.to_csv(output_path)

    return output


def myTSNE(vecs, words):
    """
    A function that performs the TSNE dimensionality
    reduction. Essentially a specialised wrapper for
    the scikit-learn TSNE

    Parameters
    ----------
    vecs : np.array
        an array of vectors from the fastText embeddings
    words : np.array
        an vector containing the strings that correspond
        to the embeddings

    Returns
    -------
    pandas.core.frame.DataFrame
        returns a dataframe which contains the 2 dimenstions
        that the TSNE reduced to as well as the strings in the
        third column

    """
    tsne = TSNE(n_components=2, verbose=1, perplexity=40, n_iter=1000)
    tsne_results = tsne.fit_transform(vecs)

    x = pd.DataFrame(tsne_results[:, 0])
    y = pd.DataFrame(tsne_results[:, 1])

    data_and_labels = pd.concat([x, y, words], axis=1)
    data_and_labels.columns = ["x", "y", "words"]
    return data_and_labels


def plot_embedding(df):
    """
    given a dataframe of size n x 3 with columns
    x, y and 'words' it will plot the x and y scatter
    plot and use the 'words' column to label each.
    Plotting done in bokeh.

    Outputs are saved into 'embeddings_plot.html'

    Parameters
    ----------
    df : pandas.core.frame.DataFrame
        Pandas dataframe of a certain
            shape: n x 3
            columns: 'x', 'y', 'words'

    Returns
    -------
    None
        returns none, however the plot is saved into
        embeddings_plot.html as a 1k by 1k pixel sized
        bokeh plot. Sizing mode is set to 'stretch_both'
        so this can be embedded and will occupy the parent
        space in presentations/websites/webapps

    """
    # convert df to bokeh objecta
    source = ColumnDataSource(df)

    p = figure(plot_width=1000, plot_height=1000,  sizing_mode='stretch_both')
    p.scatter(x='x', y='y', source=source)

    labels = LabelSet(x='x', y='y', source=source,
                      text='words', x_offset=0, y_offset=0)
    p.add_layout(labels)
    with open('embeddings_plot.html'):
        output_file('embeddings_plot.html')
        save(p)
    # LabelSet.render_mode


def plot(series, model, output_path='', cleaner=default_cleaner):
    """
    Wrapper/coordinator for the process of plotting.
    By providing some information about the model to use,
    which strings to embed and how to clean them beforehand
    this will produce a html output with embeddings plotted
    in a two dimensional scatter plot.

    The dimensional reduction
    technique used here is TSNE(perplexity=40, n_iter=1000)

    Parameters
    ----------
    series : pd.core.series.Series
        a pandas series with the strings that you want to
        embed.
    model : str | fastText model
        a string or loaded fastText model to use for embeddings
    output_path : str
        if provided, this path will be used to save a csv
        containing the original (cleaned) strings and
        the corresponding embeddings
    cleaner : func
        a function to use to clean the strings.
        the function should have a type of
            func :: str -> str

    Returns
    -------
    em
        returns the embedded vectors and strings.
        this is the same output that gets saved if
        output_path is provided.

    """

    em = embed_words(series, model, cleaner, output_path)
    tsne = myTSNE(em.iloc[:, 1:], em.iloc[:, 0])
    plot_embedding(tsne)
    return em


if __name__ == '__main__':
    print("Not to be run standalone")
