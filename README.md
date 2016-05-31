#NASS Search

A tool to search NHTSA's NASS database as well as export the data

###SETUP:

1. Open a command window and run `pip install -r requirements.txt`
 1. To use pip, Python must be installed and the Python directory should be on the PATH variable.
2. Download the NASS database folders (the folders with the names of the years) from the FTP and put them in a folder
 1. The FTP site can be found here ftp://ftp.nhtsa.dot.gov/NASS/
3. Configure user preferences (specifically the folder for the databases downloaded)
 1. User preferences are configured in each script individually through calls to nassGlobal.py's `updateUserPrefs`
4. Run `python OpenNASS.py preprocess`
 1. This will create the preprocessed index of all the databases
 2. Hit y to extract all self-extracting archives if you trust the source of your database files.

###RUN THE GUI

1. Run `python OpenNASS.py run`

###CREATE A PROGRAM:

1. See nass.py for details
