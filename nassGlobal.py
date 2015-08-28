import os.path
import json

#Common variables and data
prefs = {}
#Root folder to search
prefs["rootPath"] = os.path.normpath("./nassDB")
#Directories that we're looking for in the nassDB folder
prefs["dataDirNames"] = [
"ASCII",
"Unformatted Data",
"Expanded SAS",
os.path.normpath("Expanded SAS/UNFORMATTED")]
#Keys kept for stub cases
prefs["stubKeys"] = ["CASENO", "PSU", "VEHNO", "OCCNO"]

data = {}

fstaticDBInfo = open("staticDBInfo.json", "r")
data["staticDBInfo"] = json.loads(fstaticDBInfo.read())

#Common functionality
def userYN(msg):
    while True:
        userIn = input(msg)
        if userIn.lower() == "y":
            return True
        elif userIn.lower() == "n":
            return False
        
        print("Invalid response, please choose y or n")