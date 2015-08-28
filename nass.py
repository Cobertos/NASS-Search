import json

from nassGlobal import prefs, data
from nassDB import NASSDB
from nassSearchTerm import NASSSearchTerm, NASSSearch
from nassCase import NASSCase

#Go into each file and get column info on each db
#Present this to user and let them form a search
#Take this search back to the database and search

#Search
#Find relative database for search
#Search those databases to find the casenos of all relevant data
#Take those casenos and search all other databases for their information

def areEq(foundValue,findValue):
    return foundValue == findValue

search = NASSSearch(NASSSearchTerm.fromStrList(
("acc_desc.sas7bdat","CASENO",1, areEq)
))

fpreprocessDBInfo = open("./preprocessDBInfo.json","r")
data["preprocessDBInfo"] = json.loads(fpreprocessDBInfo.read())


if __name__ == "__main__":
    print("NASS Search Tool (c) Peter Fornari 2015\nMilestone 3: Prints all records matching a given search\n")
    
    #Go through each year and each DB in that year
    for year, yearInfo in data["preprocessDBInfo"].items():
        for dbName, dbInfo in yearInfo["dbs"].items():
            #Relevant to search?
            relevantTerms = search.ofDB(dbName)
            if len(relevantTerms) == 0:
                continue #Not a relevant database
            
            #Open the database and get cases
            nassDB = NASSDB(dbInfo)
            staticDBInfo = data["staticDBInfo"]["dbs"][dbName]
            
            printStr = year + "  \"" + staticDBInfo["prettyName"] + "\" @ \"" + ((dbInfo["filePath"][:35] + '..') if len(dbInfo["filePath"]) > 35 else dbInfo["filePath"]) + "\""
            if not nassDB.valid:
                print("[_] " + printStr)
                continue    
            print("[x] " + printStr)
    
            cases = nassDB.getCases(stubs=True,search=relevantTerms)
            search.fromDB(cases)
    
    search.finalize()
    
    '''print("Outputting matches")
    f = open("output.txt", "w")
    for caseNum, case in casesFound.items():
        s = "\n------CASENO: " + str(caseNum) + "--------\n"
        substr = ""
        for k, v in case.items():
            substr += "[" + str(k) + " = " + str(v) + "]     "
            if len(substr) > 200:
                s += substr + "\n"
                substr = ""
        s += substr
        
        f.write(s)'''

    print("Success!")