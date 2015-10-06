import os.path
import json

#Default configuration
#USER PREFERENCES
prefs = {}
#Folders and files configuration
prefs["rootPath"] = os.path.realpath(".")
prefs["dbPath"] = os.path.join(prefs["rootPath"], "nassDB")
prefs["configPath"] = prefs["rootPath"]

prefs["preprocessJSONFile"] = os.path.join(prefs["configPath"], "preprocessDBInfo.json")
prefs["staticJSONFile"] = os.path.join(prefs["configPath"], "staticDBInfo.json")

#Directories that we're looking for in the nassDB folder
prefs["dataDirNames"] = [
"ASCII",
"Unformatted Data",
"Expanded SAS",
os.path.normpath("Expanded SAS/UNFORMATTED")]

#Keys kept for stub cases
prefs["stubKeys"] = ["CASENO", "PSU", "VEHNO", "OCCNO"]

#Default compare functions
#TODO: Shouldn't go in API, should be in web application
def stringIn(found, find):
    return find in found
def equal(found, find):
    return find == found
def startsWith(found, find):
    return found.startsWith(find)
prefs["supportedCompareFuncs"] = {name : globals()[name] for name in ["stringIn", "equal", "startsWith"]}

#GLOBAL DATA
data = {}

#COMMON FUNCTIONALITY
def userYN(msg):
    while True:
        userIn = input(msg)
        if userIn.lower() == "y":
            return True
        elif userIn.lower() == "n":
            return False
        
        print("Invalid response, please choose y or n")


#Allow user to pass custom preferences
def init(userPrefs):
    #Join the user prefs over the default prefs
    prefs.update(userPrefs)

    #GLOBAL DATA
    #Json info on dbs
    fstaticDBInfo = open(prefs["staticJSONFile"], "r")
    data["staticDBInfo"] = json.loads(fstaticDBInfo.read())

    if not os.path.isfile(prefs["preprocessJSONFile"]):
        raise RuntimeError("No preprocessDBInfo found! Run the preprocessor first!")
    else:
        fpreprocessDBInfo = open(prefs["preprocessJSONFile"],"r")
        data["preprocessDBInfo"] = json.loads(fpreprocessDBInfo.read())