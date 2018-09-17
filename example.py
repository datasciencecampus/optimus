import pandas as pd

from optimus import Optimus



#### EXAMPLE OF USE

# Either:
#### 1. for a pandas Series

print(text_1)

text = pd.Series(['chocolate', 'chocolate biscuits', 'frozen pizza', 'frozn pizza', 'cleaning products',
                 'household goods', 'bicycle parts', 'mortorbike', 'cleaning brush', '3 x cars',
                 '4 x cars', 'Vauxhaul Astra', 'Toyota Yaris', 'Yaris', 'mondeo', 'Compressed gas',
                 'Helium tanks', 'frozen foods', 'foodstuff', 'groupage', 'bread and pasta', 'bread',
                 'milk', 'powder', 'baby food', 'board', ' oxygen cylinders', 'methane', 'argon', 'fertilizers',
                 'steel gates', 'metal', 'scrap metal', 'steel posts', 'fences and steel Products', 'tomatoes',
                 'potatoes', 'cleaning tools', 'building materials', 'frozen meat', 'argon', 'helium cylinders',
                 'household products', 'construction materials', 'confectionary', 'stome and paving','tractors x 3',
                 'animal products', 'composite materials', 'Plasterboard', 'cardboard'])


#### 2. from file
#### to read from file 'words.csv' in the data folder - and convert to pandas Series

text_1 = pd.read_csv("./data/words.csv", index_col=False, header=0)
text_1 = pd.Series(text_1.iloc[:,0])



#### Initialise Optimus object and run model

o = Optimus(config_path='config.json', cutoff = 6, stepsize = 1)

results = o(text_1, save_csv=True, full = True, verbose = True, runKNN=False)

results.sort_values("current_labels")
