import os.path
import json

#DummyDict - An object that will init nassGlobal when accessed
#Only implements __getitem__ so should be read only
inited = False
class DummyDict():
    def __init__(self, target):
        self.target = target
    
    def noCheck__getitem__(self, key):
        return self.target[key]
        
    def __getitem__(self, key):
        #Init if not init'd then replace with normal function
        if not inited:
            init()
            self.__getitem__ = self.noCheck__getitem__
        return self.target[key]
    
#PassThroughDict - Dictionary that will __getitem__ the values of a different dict if they exist
#The point is to fill this dict with desired values calulated from other dict values but being able to have 
class PassThroughDict(dict):
    def __init__(self, target, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.target = target
        
    def __getitem__(self, key):
        if key in self.target:
            return self.target.__getitem__(key)
        return dict.__getitem__(self, key)
    
    #Turn this dict back into a normal dict, overwriting all values with the ones in target dict
    def finalizeDict(self):
        self.update(self.target)
        self.__getitem__ = dict.__getitem__
        
#Default configuration
#USER PREFERENCES
userPrefs = {}
_prefs = PassThroughDict(userPrefs)
prefs = DummyDict(_prefs)

#GLOBAL DATA
_data = {}
data = DummyDict(_data) 
        
#Allow user to pass custom preferences
def updateUserPrefs(moreUserPrefs):
    #They can only update the preferences (or should only update them) when we haven't init'd
    if inited:
        raise RuntimeError("NASS has already been inited. User preferences shouldn't be changed now")
    
    #Join the user prefs over the default prefs
    userPrefs.update(moreUserPrefs)

#Init global data
def init():
    #USER PREFERENCES
    #Folders and files configuration
    _prefs["rootPath"] = os.path.realpath(".")
    _prefs["dbPath"] = os.path.join(_prefs["rootPath"], "nassDB")
    _prefs["configPath"] = _prefs["rootPath"]

    _prefs["preprocessJSONFile"] = os.path.join(_prefs["configPath"], "preprocessDBInfo.json")
    _prefs["staticJSONFile"] = os.path.join(_prefs["configPath"], "staticDBInfo.json")

    #Directories that we're looking for in the nassDB folder
    _prefs["dataDirNames"] = [
    "ASCII",
    "Unformatted Data",
    "Expanded SAS",
    os.path.normpath("Expanded SAS/UNFORMATTED")]

    #Keys kept for stub cases
    _prefs["stubKeys"] = ["CASENO", "PSU", "VEHNO", "OCCNO"]

    #Default compare functions
    #TODO: Shouldn't go in API, should be in web application
    def stringIn(found, find):
        return find in found
    def equal(found, find):
        return find == found
    def startsWith(found, find):
        return found.startsWith(find)
    _prefs["supportedCompareFuncs"] = {
        "String Inside" : stringIn,
        "Equal" : equal,
        "Starts With" : startsWith
    }
    _prefs.finalizeDict()
    
    #GLOBAL DATA
    #Json info on dbs
    fstaticDBInfo = open(_prefs["staticJSONFile"], "r")
    _data["staticDBInfo"] = json.loads(fstaticDBInfo.read())

    if not os.path.isfile(_prefs["preprocessJSONFile"]):
        raise RuntimeError("No preprocessDBInfo found! Run the preprocessor first!")
    else:
        fpreprocessDBInfo = open(_prefs["preprocessJSONFile"],"r")
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
