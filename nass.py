import json
import os
import re

from nassDB import NASSDB, NASSDBData

#Go into each file and get column info on each db
#Present this to user and let them form a search
#Take this search back to the database and search

#Search
#Find relative database for search
#Search those databases to find the casenos of all relevant data
#Take those casenos and search all other databases for their information

rootPath = "./nassDB/"

dataDirNames = ["ASCII", "Formatted Data", "Expanded SAS"]

fjsonDBInfo = open("nassDBInfo.json", "r")
jsonDBInfo = json.loads(fjsonDBInfo.read())

#Find all the important files within a year directory
def findYearFiles(rootYearPath):
    paths = {}
    
    paths["formats"] = None #TODO: Implement
    paths["dbs"] = [] #List of tuples with (filepath, dbInfo)
    
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
            for info in jsonDBInfo["dbs"]:
                if entry == info["fileName"]:
                    paths["dbs"].append((dbPath + entry,info))
                    break
    
    return paths
    
if __name__ == "__main__":
    print("NASS Search Tool (c) Peter Fornari 2015\nMilestone 2: Print all records for multiple years\n")
    
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
        
        casesFound = {}
        for db in files["dbs"]:
            data = NASSDBData(db[0])
            nassDB = NASSDB(data)
            
            if not nassDB.valid:
                print("[_] " + year + "  \"" + db[1]["prettyName"] + "\" @ \"" + ((db[0][:35] + '..') if len(db[0]) > 35 else db[0]) + "\"")
                continue
                
            print("[x] " + year + "  \"" + db[1]["prettyName"] + "\" @ \"" + ((db[0][:35] + '..') if len(db[0]) > 35 else db[0]) + "\"")
            
            cases = nassDB.getCases(stubs=True)
            for caseNum, case in cases.items():
                if not caseNum in casesFound:
                    casesFound[caseNum] = case
                else:
                    casesFound[caseNum].update(case)
        
        print("Outputting matches")
        f = open("output" + year + ".txt", "w")
        for caseNum, case in casesFound.items():
            s = "\n------CASENO: " + str(caseNum) + "--------\n"
            substr = ""
            for k, v in case.items():
                substr += "[" + str(k) + " = " + str(v) + "]     "
                if len(substr) > 200:
                    s += substr + "\n"
                    substr = ""
            s += substr
            
            f.write(s)

        print("Success!")