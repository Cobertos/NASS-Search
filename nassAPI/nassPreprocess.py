import json
import os
import re
import subprocess

from . import nassGlobal
from .nassGlobal import prefs, data
from .nassDB import NASSCaseDB

#Preprocesses the NASSDB folder for everything that's there
#Currently throws everything into a JSON file pretty printed
#Will also extract Self-Extracting archives with users consent (because we're running arbitrary exes in the filesystem)

#Preprocessor filters and generates data based on a few things (if you can't figure out why it won't include some dbs)
#A database is only read if it occurs in one of the prefs["dataDirNames"] directories
#A database is only read if it occurs in the staticDBInfo.json file
#A database is only read if it ends in .sas7bdat
#Columns of a database are gathered from NASSCaseDB (so it is allowed to filter/condense column names as it sees fit)

#Find all the important files within a year directory
def findYearFiles(year, rootYearPath):
    paths = {}
    
    paths["formats"] = None #TODO: Implement, eventually a list of (filepaths)
    paths["linksDB"] = None #The database that contains the relations between cases and the link ID for the NASS case viewer
    paths["dbs"] = {} #List of dictionaries with {filename, filepath, columnList} keys
    
    #Links DBs
    #The db to get the links is in the base of the directory and the same name as the year path
    linksDB = "case" + year + ".sas7bdat"
    linksDBPath = os.path.join(rootYearPath, linksDB)
    if os.path.isfile(linksDBPath):
        paths["linksDB"] = linksDBPath
        print("Found links DB: " + linksDB)
    else:
        print("## Could not find links database")
    
    #DBs
    #Currently only finds dataDir (DB) folders and adds the files that match up with databases in the database info file
    for entry in prefs["dataDirNames"]: #Only search for these folders
        dbPath = os.path.join(rootYearPath, entry)
        if not os.path.isdir(dbPath):
            continue
        
        print("Found DB directory: " + dbPath)
        
        def getExt(entry):
            dotPos = entry.find(".")
            if dotPos == -1:
                return None
            return entry[dotPos+1:]
        
        #First check for a WinZip Self-Extracting Archive
        for entry in os.listdir(dbPath):
            entryFilePath = os.path.join(dbPath, entry)
            if not os.path.isfile(entryFilePath):
                continue
            
            extension = getExt(entry)
            if extension != "exe":
                continue
                
            #There's no good test to see if it's a WinZip self-extracting archive (confirmed by WinZip support)
            print("Found possible WinZip self-extracting archive \"" + entry + "\".")
            print("Executables are not automatically run for safety. Only run if you trust your source of NASS data.")
            yn = nassGlobal.userYN("Would you like to run this file? [y or n]: ")
            if yn:
                #The /auto runs with no prompt, '.' extracts to the current directory
                subprocess.call([entryFilePath, "/auto", "."])
                print("Extracted.")
                os.remove(entryFilePath)
                print("Deleted.")
            else:
                print("Skipped.")
            continue
        
        #Now check if the folder has any valid databases in it
        for entry in os.listdir(dbPath):
            entryFilePath = os.path.join(dbPath, entry)
            if not os.path.isfile(entryFilePath):
                continue
            
            extension = getExt(entry)
            if extension != "sas7bdat":
                continue
                
            #Check and make sure it's a file we have defined as a db
            if not entry in data["staticDBInfo"]["dbs"].keys():
                continue
                
            #See if valid database
            try:
                dbData = NASSCaseDB.getData(entryFilePath, year=year)
            except:
                continue
            
            paths["dbs"][entry] = dbData
            print("Found DB: " + entryFilePath)
                    
    return paths

def main():
    #Year information
    years = {}

    #For every year directory
    for entry in os.listdir(prefs["dbPath"]):
        if not os.path.isdir(os.path.join(prefs["dbPath"],entry)) or not re.match('\d{4}', entry, re.I):
            continue
        
        #Resolve directories in this directory that contain data
        year = entry
        files = findYearFiles(year, os.path.join(prefs["dbPath"],entry))
        
        if len(files["dbs"]) == 0:
            print("Could not resolve any db files for " + year)
            continue
        
        years[year] = files
        
    #Output everything as JSON
    f = open(prefs["preprocessJSONFile"], "w")
    f.write(json.dumps(years, sort_keys=True, indent=4, separators=(',', ': ')))
    
if __name__ == "__main__":
    main()
    