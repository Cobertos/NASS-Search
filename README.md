#NASS Search

A tool to search NHTSA's NASS database as well as export the data

###SETUP:

1. Open a command window and run `pip install -r requirements.txt`
 1. To use pip, Python must be installed and the Python directory should be on the PATH variable.
2. Download the NASS database folders (the folders with the names of the years) from the FTP and put them in a folder
3. Configure user preferences (specifically the folder for the databases downloaded)
 1. User preferences are configured in each script individually through calls to nassGlobal.py's `updateUserPrefs`
4. Run `python nassPreprocess.py`
 1. This will create the preprocessed index of all the databases
 2. Hit y to extract all self-extracting archives if you trust the source of your database files.

###RUN THE GUI

1. Open a command window and navigate to `./nassWebApp`
2. Run `python nassFlaskWeb.py`
3. The Flask web server should now be running.
3. Open a browser and navigate to `127.0.0.1:5000`
4. Use the GUI to perform searches.

###CREATE A PROGRAM:

1. See nass.py for details
