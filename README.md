NASS Search

A tool to search NHTSA's NASS database as well as export the data

SETUP:

1. Run `pip install -r requirements.txt`
2. Download the NASS database folders (the folders with the names of the years) from the FTP and put them in a folder
3. Configure user preferences through calls to nassGlobal.py's `updateUserPrefs`
4. Run `python nassPreprocess.py` (hit y to extract each self extracting archive)

CREATE A PROGRAM:

1. See nass.py for details

RUN THE GUI

1. Open a command window and go to `./nassWebApp`
2. Run `python nassFlaskWeb.py`
3. Open a browser and navigate to `127.0.0.1:5000`
