import json

from nassAPI.nassSearchTerm import NASSSearchTerm, NASSSearch
from nassAPI.nassCase import NASSCase

#Go into each file and get column info on each db
#Present this to user and let them form a search
#Take this search back to the database and search

#Search
#Find relative database for search
#Search those databases to find the casenos of all relevant data
#Take those casenos and search all other databases for their information

def areEq(foundValue,findValue):
    return foundValue == findValue
def strIn(foundValue,findValue):
    return findValue in foundValue

search = NASSSearch(NASSSearchTerm.fromStrList([
("acc_desc.sas7bdat","LINETXT","dog", strIn), "OR",
("acc_desc.sas7bdat","LINETXT","pet", strIn)
]))



if __name__ == "__main__":
    print("NASS Search Tool (c) Peter Fornari 2015-2016\n")
    
    search.perform()
    cases = search.export("links")
    
    print("Outputting matches")
    f = open("output.txt", "w")
    for case, link in cases:
        f.write("\n" + ("="*110) + "\n" + case.prettyPrint(fixedLen=100) + "\n" + link)

    print("Success!")