import json

from nassGlobal import prefs, data
from nassDB import NASSDB
from nassSearchTerm import NASSSearchTerm
from nassCase import NASSCase

#Go into each file and get column info on each db
#Present this to user and let them form a search
#Take this search back to the database and search

#Search
#Find relative database for search
#Search those databases to find the casenos of all relevant data
#Take those casenos and search all other databases for their information

search = NASSSearch(NASSSearchTerm.fromStrList([
("acc_desc.sas7bdat","CASENO","value"), "AND" ("thisOne")
]))

fpreprocessDBInfo = open("./preprocessDBInfo.json","r")
data["preprocessDBInfo"] = json.loads(fpreprofessDBInfo.read())


if __name__ == "__main__":
    print("NASS Search Tool (c) Peter Fornari 2015\nMilestone 2: Print all records for multiple years\n")
    
    matchingCases = {}
    for year, yearInfo in data["preprocessDBInfo"]["years"].items():
        
        yearMatchingCases = None
        for dbInfo in yearInfo:
            relevantTerms = term.ofDB(dbInfo["fileName"])
            if len(relevantTerms) == 0:
                continue #Not a relevant database
            
            nassDB = NASSDB(dbInfo)

            staticDBInfo = data["staticDBInfo"][dbInfo["fileName"]]
            if not nassDB.valid:
                print("[_] " + year + "  \"" + staticDBInfo["prettyName"] + "\" @ \"" + ((dbInfo["filePath"][:35] + '..') if len(dbInfo["filePath"]) > 35 else dbInfo["filePath"]) + "\"")
                continue
                
            print("[x] " + year + "  \"" + staticDBInfo["prettyName"] + "\" @ \"" + ((dbInfo["filePath"][:35] + '..') if len(dbInfo["filePath"]) > 35 else dbInfo["filePath"]) + "\"")
    
            cases = nassDB.getCases(stubs=True,search=relevantTerms)
            if yearMatchingCases == None:
                yearMatchingCases = cases
            else:
                yearMatchingCases.extend(cases)
        
        matchingCases[year] = yearMatchingCases
    
    
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