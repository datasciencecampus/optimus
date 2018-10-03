# Optimus-launcher app documentation


### Quickstart
If you would like to skip the following chapter of manual installation, you can execute the quickstart.sh file from a shell terminal by typing in `sh quickstart.sh` which should get you up and running.

The script will:
  1. preinstall the required python dependencies,
  2. navigate to the root optimus folder
  3. run the app
  4. open the required url in your browser.

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

1. After ensuring the app runs, the next step is to upload the data.
Click the 'Upload string data' button. Then navigate to the location of the relevant csv file. After confirming a preview of the data should appear in the bottom of the app.

2. After the data has been loaded the next step is to configure the optimus object. There are 2 ways of doing so.
   * The first way to configure optimus is mostly useful if there are only a few settings that you would like to change. In which case use the predefined boxes with the appropriate setting names.

   * However if more changes to the detailed settings are required input them into the free text field. The format for the settings to be passed is as follows `setting1:value,setting2:value`. Note, there is no comma at the end of the settings as the parser for settings is fairly rudimentary.  


   ##### NOTE:
   A model path **MUST** be provided regardless if one uses the predefined boxes or not. The path should be a full path in the form of /Users/myuser/path/to/wiki.en.bin

3. Once settings have been entered click 'upload settings'
4. Finally click 'Run optimus pipeline'
