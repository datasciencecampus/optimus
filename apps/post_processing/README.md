# Optimus post-processing app documentation
# NOTE:
The UI and UX of the app are very experimental. They are subject to change quite substantially in the remaining time that this app will be supported/developed. Feedback on this is appreciated.
## Quickstart (Linux and MacOS)
A `quickstart.sh` script is provided within the app folder. This script will install the required python dependencies and will run the app automatically and open the browser to the app window.

**NOTE:** set up the config.json file beforehand to point to the correct dataset path.
## The manual set up
In order for the app to run correctly you will need python 3 and the following python modules:
```
dash
dash-core-components
dash-html-components
dash-table-experiments
plotly
flask
pandas
```
In order to quickly install this run the following command in while in the app folder:
```
pip install -r requirements
```
The app is then ready to launch by simply tweaking the config.json file and by launching the app from the terminal as follows:
```
cd path/to/app/folder
python app.py
```
## Configuring the app
In order to configure the app open the `config.json` file with a text editor of your choice. The following settings will define how the app functions:

```json
{
  /* The location of the file which
  will be used as a basis for the
  processing. See further notes on the
  expected structure of this file*/
  "data":"",
  /* The path to the output file (csv)*/
  "out":"output.csv",
  /* Clusters smaller than this value
  will be skipped in the app and assigned
  a 'SKIPPED' label*/
  "min_cluster":15,
  /* A predefined selection of categories
  to provide to the user in the dropdown
  on start up */
  "options":[],
  /* Defines if smart labelling is
  enabled (EXPERIMENTAL). See further
  for explanation of what this means. */
  "smart_labeling":false,
  /* Number of tiers to display, this
  doesn't affect which tiers you can choose
  it is mainly to stop the data table
  being too massive */
  "tiers":2

}
```
### Expected input file structure
The expects a certain structure from the input csv file. The file must have a 'current_label' column and can have several 'tier_n' columns. The structure of the file with which this app was developed was as follows:

| original   | tier_1 | tier_2 | ... | tier_n | current_labels |
|------------|--------|--------|-----|--------|----------------|
| string1    | ...    | ...    | ... | ...    | ...            |
| string2    | ...    | ...    | ... | ...    | ...            |
| string3    | ...    | ...    | ... | ...    | ...            |

A file output from a full Optimus pipeline will work and is what was used to build this app.

NOTE: when the data is presented for the user, on first glance it may seem like it only displays 150 rows per cluster. The
rest of the data will still be displayed upon scrolling through the table, however the size of the table will not accommodate
these extra entries.

### Smart labelling
This feature checks the custom class input provided by user and if it finds any clusters in the dataset which have that same exact current_label as the newly provided class it will also accept these. This is particularly useful in labelling datasets with simple names.

**Example:**

If a user provided new class name 'cars' any entries within the data which have the 'current_label' as 'cars' will automatically be assigned that in the 'new_label' column assuming that is an acceptable label.

This behaviour might not always be wanted.

## Usage
The app will respect the cluster size threshold provided in the config.json file. It will thus select cluster that are larger or equal that size. The selected cluster labels will be presented to the user to categorise and relabel. The non-selected cluster based on this threshold will get a new label assigned as **'SKIPPED'**

Options 1-4 of the relabelling procedures presented further will be applied to (a) the full dataset if none of the checkboxes are ticked or (b) to the rows that are selected (if any are selected). Meaning that the user can pick which rows get properly classified. Option 5 will always be applied to the whole cluster.

There are several relabelling options.
1. *Accepting the automatically assigned label.*
If the label in the current_label fit the actual contents of the cluster, then the user can simply accept the label using the **'Accept'** button and proceed to the next cluster.
2. *Rename the cluster with a arbitrary string input.*
 This string will be assigned to the 'new_label' column as soon as the user clicks **'Done'**. Note: strings added this way will be then available in the dropdown window alongside other class names.
3. *Pick one of the predefined category names*.
If the 'options' parameter in the config.json file contains a list of string category names, these will be presented to the user in the dropdown. Any entries that the user provides under option 2 will also be reflected here. The dropdown is also searchable, hence you can type a word such as 'vehicle' and it will find any category names containing this word.
4. *Pick one of the earlier tiers*
If a dataset contains columns from previous iterations (particularly relevant to the Optimus pipeline) with the labels 'tier_n', then these will be selectable in this dropdown. A user is thus able to relabel the whole cluster with a more suitable earlier iteration of the process.
5. *Skip the given cluster*
If a user is unable to relabel the cluster, they can choose to skip the cluster. To do this simply leave the dropdown for the predefined classes or the tier labelling empty and click the respective button. An empty dropdown will assign the value **'SKIPPED'** to the cluster.


Selecting any of these options will advance the process to the next cluster. However the arrow keys at the top of the page will allow to go back and forth between clusters. Thus if a mistake is made one can go back and edit a cluster again.

## Selecting individual rows

By using the tickboxes next to the data only the data that is selected will be processed. However if there is a case of a cluster similar
to:

```
['fish','meat','meat','fish']
```

If you select entries with fish and classify them into `aquatic animals` the app will push you into the next cluster and assigned `SKIPPED` but only on the first pass over the cluster. However if a user wants to also classify the `meat` as well they can use the arrows to go back and select the meat entries and assign a new label. Only those entries will be overwritten. The already existing fish labels will not be overwritten.
