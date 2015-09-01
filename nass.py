import json

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



if __name__ == "__main__":
    print("NASS Search Tool (c) Peter Fornari 2015\nMilestone 3: Prints all records matching a given search\n")
    
    search.perform()
    cases = search.export("cases")
    
    print("Outputting matches")
    f = open("output.txt", "w")
    for case in cases:
        s = "\n------------------------\n"
        substr = ""
        for db, kvs in case.dbs.items():
            substr += "[" + str(db) + "| " + str(kvs) + "]     "
            if len(substr) > 200:
                s += substr + "\n"
                substr = ""
        s += substr
        
        f.write(s)

    print("Success!")