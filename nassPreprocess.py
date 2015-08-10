import json
import os
import re

from nassGlobal import prefs, data
from nassDB import NASSDB

#Preprocesses the NASSDB folder for everything that's there
#Currently throws everything into a JSON file pretty printed

#Preprocessor relies on two things:
#The database columns are based on how NASSDB processes a database.
#The databases read is dependant on the original nassDBInfo

#Find all the important files within a year directory
def findYearFiles(rootYearPath):
    paths = {}
    
    paths["formats"] = None #TODO: Implement, eventually a list of (filepaths)
    paths["dbs"] = [] #List of dictionaries with {filename, filepath, columnList} keys
    
    #Currently only finds dataDir (DB) folders and adds the files that match up with databases in the database info file
    for entry in os.listdir(rootYearPath):
        if not os.path.isdir(rootYearPath + entry):
            continue
        
        #Make sure its in the list of data dir folders we want to process
        if not entry in dataDirNames:
            continue
        
        #Check if the folder has any valid databases in it
        dbPath = rootYearPath + entry + "/"
        for entry in os.listdir(dbPath):
            for info in data["staticDBInfo"]["dbs"]:
                if entry == info["fileName"]: #Check and make sure it's a file we have defined as a database
                    dbFilePath = dbPath + entry
                    #TODO: This is a little wonky because NASSDB expects a data object right now
                    #   Make it accept just a fp or something?
                    dbInfo = {"filePath" : dbFilePath, "fileName" : entry}
                    db = NASSDB(dbInfo)
                    if not db.valid: #Make sure it's valid
                        continue
                    
                    columns = [col.name for col in db.columns] #Get columns and filepath and store it
                    paths["dbs"].append({
                        "fileName" : entry,
                        "filePath" : dbFilePath,
                        "columnNames" : columns})
                    
    return paths
    
if __name__ == "__main__":
    #Year information
    years = {}

    #For every year directory
    for entry in os.listdir(rootPath):
        if not os.path.isdir(rootPath + entry) or not re.match('\d{4}', entry, re.I):
            continue
        
        #Resolve directories in this directory that contain data
        year = entry
        files = findYearFiles(rootPath + entry + "/")
        
        if len(files["dbs"]) == 0:
            print("Could not resolve any db files for " + year)
            continue
        
        years[year] = files
        
    #Output everything as JSON
    f = open("preprocessDBInfo.json", "w")
    f.write(json.dumps(years, sort_keys=True, indent=4, separators=(',', ': ')))
    