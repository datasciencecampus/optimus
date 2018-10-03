"""
Perform a simple random sample of your words and run optimus on the sample.
Then use a knn to put it all back together at the end.
"""

#-- Imports ---------------------------------------------------------------------
# third party
import fastText as ft
import pandas   as pd

from optimus           import Optimus
from sklearn.neighbors import KNeighborsClassifier


#-- Functions -------------------------------------------------------------------
def main():

    # load in the data, sample from it and run optimus on the sample
    words = pd.read_csv('data/words.csv', header=None, names=('description',))['description']
    sample = words.sample(1000)

    O = Optimus(config_path='config.json')
    result = O(sample)

    df_sample = pd.DataFrame({'original': sample, 'label': result})

    # use a knn on vectors + assigned labels to apply these labels to the whole dataset
    model = ft.load_model('models/wiki.en.bin')
    embedSample = [model.get_word_vector(word) for word in sample.tolist()]

    # train the model on the result and the embedded sample vectors
    classifier = KNeighborsClassifier()
    trained = classifier.fit(embedSample, result)

    nonsampled = [word for word in words.tolist() if word not in sample.tolist()]
    outvectors = [model.get_word_vector(word) for word in nonsampled]

    predictions = trained.predict(outvectors)

    df_unsampled = pd.DataFrame({'original': nonsampled, 'label': predictions})

    df = pd.concat([df_sample, df_unsampled])
    df.to_csv('output.csv', index=False)


if __name__ == '__main__':
    main()
