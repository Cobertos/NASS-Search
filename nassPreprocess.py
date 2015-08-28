import json
import os
import re
import subprocess

from nassGlobal import prefs, data
from nassDB import NASSDB

#Preprocesses the NASSDB folder for everything that's there
#Currently throws everything into a JSON file pretty printed
#Will also extract Self-Extracting archives with users consent (because we're running arbitrary exes in the filesystem)

#Preprocessor filters and generates data based on a few things (if you can't figure out why it won't include some dbs)
#A database is only read if it occurs in one of the prefs["dataDirNames"] directories
#A database is only read if it occurs in the staticDBInfo.json file
#A database is only read if it ends in .sas7bdat
#Columns of a database are gathered from NASSDB (so it is allowed to filter/condense column names as it sees fit)

#Find all the important files within a year directory
def findYearFiles(year, rootYearPath):
    paths = {}
    
    paths["formats"] = None #TODO: Implement, eventually a list of (filepaths)
    paths["dbs"] = {} #List of dictionaries with {filename, filepath, columnList} keys
    
    #Currently only finds dataDir (DB) folders and adds the files that match up with databases in the database info file
    for entry in prefs["dataDirNames"]: #Only search for these folders
        dbPath = os.path.join(rootYearPath, entry)
        if not os.path.isdir(dbPath):
            continue
        
        print("Found directory: " + dbPath)
        
        #Check if the folder has any valid databases in it
        for entry in os.listdir(dbPath):
            dbFilePath = os.path.join(dbPath, entry)
            if not os.path.isfile(dbFilePath):
                continue
                
            #Check and make sure it's a sas7bdat file
            dotPos = entry.find(".")
            if dotPos == -1:
                continue
            extension = entry[dotPos+1:]
            #WinZip Self-Extracting Archives
            if extension == "exe":
                #TODO: Do the extraction
                #Alert the user they're running an exe named whatever
                #subprocess.call([entry, "/auto", "."])
                continue
            if not extension == "sas7bdat":
                continue
                
            #Check and make sure it's a file we have defined as a db
            if not entry in data["staticDBInfo"]["dbs"].keys():
                continue
                
            #TODO: This is a little wonky because NASSDB expects a data object right now
            #   Make it accept just a fp or something?
            dbInfo = {"filePath" : dbFilePath, "fileName" : entry}
            db = NASSDB(dbInfo)
            if not db.valid: #Make sure it's valid
                continue
            
            columns = [col.name for col in db.columns] #Get columns and filepath and store it
            paths["dbs"][entry]= {
                "year" : year,
                "fileName" : entry,
                "filePath" : dbFilePath,
                "columnNames" : columns}
            print("Found file: " + dbFilePath)
                    
    return paths
    
if __name__ == "__main__":
    #Year information
    years = {}

    #For every year directory
    for entry in os.listdir(prefs["rootPath"]):
        if not os.path.isdir(os.path.join(prefs["rootPath"],entry)) or not re.match('\d{4}', entry, re.I):
            continue
        
        #Resolve directories in this directory that contain data
        year = entry
        files = findYearFiles(year, os.path.join(prefs["rootPath"],entry))
        
        if len(files["dbs"]) == 0:
            print("Could not resolve any db files for " + year)
            continue
        
        years[year] = files
        
    #Output everything as JSON
    f = open("preprocessDBInfo.json", "w")
    f.write(json.dumps(years, sort_keys=True, indent=4, separators=(',', ': ')))
    