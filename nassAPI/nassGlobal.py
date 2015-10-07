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
_data = {}
inited = False

#Fake data class to redirect data accesses to _data with some checks
class dummyData():
    def nonInitGetItem(self, key):
        return _data.__getitem__(key)

    def __getitem__(self, key):
        #Init if not init'd then replace with normal function
        if not inited:
            init()
            self.__getitem__ = self.nonInitGetItem
        return _data.__getitem__(key)
    def __setitem__(self, key, item):
        _data.__setitem__(key, item)
data = dummyData()

    
        
#Allow user to pass custom preferences
def userPrefs(userPrefs):
    #They can only update the preferences (or should only update them) when we haven't init'd
    if inited:
        raise RuntimeError("NASS has already been inited. User preferences shouldn't be changed")
    
    #Join the user prefs over the default prefs
    prefs.update(userPrefs)

#Init global data
def init():
    #GLOBAL DATA
    #Json info on dbs
    fstaticDBInfo = open(prefs["staticJSONFile"], "r")
    _data["staticDBInfo"] = json.loads(fstaticDBInfo.read())

    if not os.path.isfile(prefs["preprocessJSONFile"]):
        raise RuntimeError("No preprocessDBInfo found! Run the preprocessor first!")
    else:
        fpreprocessDBInfo = open(prefs["preprocessJSONFile"],"r")
        _data["preprocessDBInfo"] = json.loads(fpreprocessDBInfo.read())
        

#COMMON FUNCTIONALITY
def userYN(msg):
    while True:
        userIn = input(msg)
        if userIn.lower() == "y":
            return True
        elif userIn.lower() == "n":
            return False
        
        print("Invalid response, please choose y or n")
