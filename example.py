import pandas as pd

from optimus import Optimus

text = pd.Series(['chocolate', 'chocolate biscuits', 'frozen pizza', 'frozn pizza', 'cleaning products',
                 'household goods', 'bicycle parts', 'mortorbike', 'cleaning brush', '3 x cars',
                 '4 x cars', 'Vauxhaul Astra', 'Toyota Yaris', 'Yaris', 'mondeo', 'Compressed gas',
                 'Helium tanks', 'frozen foods', 'foodstuff', 'groupage', 'bread and pasta', 'bread',
                 'milk', 'powder', 'baby food', ' oxygen cylinders', 'methane', 'argon', 'fertilizers',
                 'steel gates', 'metal', 'scrap metal', 'steel posts', 'fences and steel Products'])



o = Optimus(config_path='config.json', cutoff = 6, stepsize = 1)

results = o(text, save_csv=True, full = True, verbose = True, runKNN=False)
