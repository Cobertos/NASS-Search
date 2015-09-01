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
    print("NASS Search Tool (c) Peter Fornari 2015\nMilestone 4: Searching and exporting to links format\n")
    
    search.perform()
    cases = search.export("links")
    
    print("Outputting matches")
    f = open("output.txt", "w")
    for case, link in cases:
        f.write("\n------------------------\n" + case.prettyPrint(fixedLen=200) + "\n" + link)

    print("Success!")