# Optimus-launcher app documentation
# NOTE:
The UI and UX of the app are very experimental. They are subject to change quite substantially in the remaining time that this app will be supported/developed. Feedback on this is appreciated.

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
Note: This assumes you are in the apps/pipeline_launcher folder in the terminal window.
If you have opened the terminal in the root folder of optimus enter this command before
typing in the aformentioned one:
```
cd ./apps/pipeline_launcher
```

The app is then ready to launch by simply typing these commands into a terminal as follows:
```
python app.py
```

## Usage
