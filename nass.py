import json
import os
import re

from nassDB import NASSDB, NASSDBData

#Go into each file and get column info on each db
#Present this to user and let them form a search
#Take this search back to the database and search

#Search
#Find relative database for search
#Search those databases to find the caseids of all relevant data
#Take those caseids and search all other databases for their information

'''class SearchTerm():
    def __init__(self, dbName, colName, searchValue, compareFunc):
        self.dbName = dbName
        self.colName = colName
        self.searchValue = searchValue
        self.compareFunc = compareFunc
    
    def compare(self, value):
        return self.compareFunc(value, self.searchValue)

'''

if __name__ == "__main__":
    print("NASS Search Tool (c) Peter Fornari 2015\nMilestone 2: Print all records for multiple years\n")
    
    rootPath = "./nassDB/"
    fDBInfo = open("nassDBInfo.json", "r")
    dbInfo = json.loads(fDBInfo.read())
    
    uDataDirNames = ["ASCII", "Formatted Data", "Expanded SAS"]
    
    #For every year directory
    for obj in os.listdir(rootPath):
        if not os.path.isdir(rootPath + obj) or not re.match('\d{4}', obj, re.I):
            continue
        
        #Resolve directories in this directory that contain data
        year = obj
        yearPath = rootPath + obj + "/"
        dataPath = None
        
        for obj in os.listdir(yearPath):
            if not os.path.isdir(yearPath + obj):
                continue
            
            if obj in uDataDirNames:
                dataPath = yearPath + obj + "/"
                continue
        
        if not dataPath:
            print("Could not resolve data path for " + year)
            continue
            
        #Go through the data directory for databases
        for obj in os.listdir(dataPath):
            if not os.path.isfile(dataPath + obj):
                continue
            
            #Only use known DBs
            currDBInfo = None
            for info in dbInfo["dbs"]:
                if obj == info["fileName"]:
                    currDBInfo = info["fileName"]
                    break
            else:
                continue
            
            dbPath = dataPath + obj
            print("Found " + currDBInfo["prettyName"] + " in " + dbPath)
            
            casesFound = {}
            data = NASSDBData(dbPath)
            nassDB = NASSDB(data)
            cases = nassDB.getCases(stubs=True)
            for caseNum, case in cases.items():
                if not caseNum in casesFound:
                    casesFound[caseNum] = case
                else:
                    casesFound[caseNum].update(case)
                    
        print("Outputting matches")
        f = open("output.txt", "w")
        for caseNum, case in casesFound.items():
            s = "\n------CASEID: " + caseNum + "--------\n"
            substr = ""
            for k, v in case.items():
                substr += "[" + str(k) + " = " + str(v) + "]     "
                if len(substr) > 200:
                    s += substr + "\n"
                    substr = ""
            s += substr
            
            f.write(s)

        print("Success!")




    '''print("Searching DBs")
    def matchIt(src, test):
        return test in src

    searchTerms = [
        SearchTerm("acc_desc", "TEXT71", "dog", matchIt),
        SearchTerm("typ_acc", "TEXT66", "dog", matchIt),
        SearchTerm("veh_pro", "TEXT81", "dog", matchIt),
        SearchTerm("pers_pro", "TEXT91", "dog", matchIt)
    ]

    matches = []
    for dbName, db in dbs.items():
        sts = []
        for st in searchTerms:
            if st.dbName == dbName:
                sts.append(st)
        
        if not sts:
            continue
        
        print("Searching: " + dbName)    
        matches += db.search(sts)

    print("Getting relevant records")
    rows = {}
    for dbName, db in dbs.items():
        print("Searching: " + dbName)
        kvs = db.getCaseIDs(matches)
        for kv in kvs:
            caseID = kv["CASEID"]
            if not caseID in rows:
                rows[caseID] = kv
            else:
                for kNew, vNew in kv.items():
                    if kNew in rows[caseID]:
                        if vNew and rows[caseID][kNew]:
                            rows[caseID][kNew] += vNew
                    else:
                        rows[caseID][kNew] = vNew
                #rows[caseID].update(kv)'''