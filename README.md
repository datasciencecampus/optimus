# O P T I M U S

A pipeline for classifying free-text strings

## Getting Started

These instructions will get you a copy of the project up and running on your local machine for development and testing purposes.

### Prerequisites

You will need the following tools in order to be able to set up and use optimus:

- A modern MacOS or linux installation, Windows is not currently supported and
  you are on your own trying it there. This will cover tools such as wget/curl
  and unzip that we require. We also need the following non-standard tools.
- [zsh](https://github.com/robbyrussell/oh-my-zsh/wiki/Installing-ZSH)
- [python 3.6](https://www.python.org) or later
- [git](https://git-scm.com)

Firstly the user should clone this git repository
```
git clone git@github.com:datasciencecampus/optimus
```

Within the repo is a file named `setup.zsh`. This is a command line tool to
install all of the other things you need. For help using this, invoke the script
as

``` sh
. setup.zsh -h
```

This script allows you to download the [FastText wikipedia word
embeddings](https://github.com/facebookresearch/fastText/blob/master/pretrained-vectors.md)
model and places it in the optimus directory. If your project is elsewhere and
you are not working in optimus directly then it is recommended to use this script to
download the model and then you can move it to be local to your working directory.


## How to use the python module

#### Importing Optimus
Import Optimus into python either through the whole module

  * `import optimus`

or by importing the Optimus classes

  * `from optimus import Optimus`

#### Customise settings for Optimus

Configuration of the pipeline is controlled with a configuration file `config.json` file in the following format:

```json
  {
    "data":"location/to/data.csv",
    "model":"location/to/wiki.en.bin"
    ...
  }
```

After creating a `config.json` file, the location can be passed when creating an instance of Optimus:

```python
o = Optimus(config_path='path/to/config.json', ...)
```

Further settings can be added on an ad hoc basis and will overwrite any previous settings. To do so, pass in valid arguments into the Optimus class upon construction like so:

```python
o = Optimus(
      config_path='path/to/config.json',
      data="path/to/new_data.csv",
      cutoff=6,
      ...
  )
```

Optimus has a default settings file to fall back on in case none of this is provided however using just default settings might cause issues. This is mainly due to the path specifications to the data and models in the default settings not being accurate.


Shortened reference:

 1. `obj = Optimus()` -> Uses default settings
 2. `obj = Optimus(config_path='path/to/user/config.json')` -> Uses custom config file
 3. `obj = Optimus(distance=10, stepsize=2, cutoff=16 ...)` -> replace specific parameter values instead of those defined in the config file.

#### Running the code & getting outputs

Optimus takes in a `pandas.core.series.Series` objects. In order to run a configured Optimus object on a series, simply call the object and enclose the desired series in the brackets.

For example, for a pandas series called `text`:

``` python
from optimus import Optimus

O = Optimus()
results = O(text)
```

**NOTE**: If no data is passed into the the Optimus object the data defined in the config file will be used.

##### Additional parameters you can pass during the aformentioned call:

* **save_csv**
One can pass "save_csv" as an optional parameter. If True this will force Optimus to save the output DataFrame which includes all the labels from each iteration in the working directory as prowl.csv


* **full**
Similarly if one just needs a dataframe to be returned and not saved, use the full=True setting to receive back the prowl dataframe.

* **verbose**
A boolean value which will dictate how much will be printed to the console as the code runs. Some outputs are still maintained in the console even if `verbose=False`

## Managing Memory

The fastText model is large and requires a sizeable chunk of RAM.

#### Note on RAM usage due to model loading

Each instance of optimus will load its own fast text model on the first processing call. It does this by checking if the model was loaded before and if not will perform a ft.load_model() operation. Once its loaded, all subsequent runs (based on the same instance of Optimus) should not reload a model.

#### Optimus.replace_model method

The optimus object has a replace_model method. This method aims to provide a way to control the memory usage of the Optimus object. This method allows a user to reload and replace a new model or just to remove the loaded model from the Optimus object.

The method takes a string or a fastText loaded model and assigns it to the Optimus object. If no model parameter is passed, the method will simply delete and garbage collect the existing loaded model.

```python
o = Optimus(args, kwargs)
output = o(some_data)

# Load from a path
o.replace_model('string/path/to/model')

# Provide an already loaded model
o.replace_model(fastText.load_model('string/path/to/model'))

# Delete the existing model in the Optimus object
o.replace_model()

```

## Authors / Contributors

#### Data Science Campus - Office for National Statistics
* Steven Hopkins
* Gareth Clews
* Arturus Eidukus
* Lucy Gwilliam

#### Department for the Environment, Food and Rural Affairs
* Tom Hopkinson

## License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details
