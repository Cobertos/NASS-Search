NASS Search

A tool to search NHTSA's NASS database as well as export the data

SETUP:
1) pip install -r requirements.txt
2) Download the NASS database folders (the folders with the names of the years) from the FTP and put them in a folder
3) Configure preferences in nassGlobal.py (including where the NASS databases are stored)
4) Run nassPreprocess.py (hit y to extract each self extracting archive)
5) Run nass.py