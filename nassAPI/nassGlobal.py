"""
NASS Search Tool Global Preferences and Data

This module holds the global preferences and data structures. All prefs & data
should be read from nassGlobal.prefs and nassGlobal.data.
"""

import os.path
import json

#DummyReadOnlyDict - A dict that once read will call init() but only once across all instances
#Only implements __getitem__ so should be read only
class DummyReadOnlyDict():
    triggered = False
    def __init__(self, target):
        self.target = target
    
    def noCheck__getitem__(self, key):
        return self.target[key]
        
    def __getitem__(self, key):
        #Multiple dicts might be accessed at different times
        #Only trigger if none before
        if not DummyReadOnlyDict.triggered:
            init()
            DummyReadOnlyDict.triggered = True
        #Replace this function with the noCheck version if a trigger has occured previously
        if DummyReadOnlyDict.triggered:
            self.__getitem__ = self.noCheck__getitem__
        return self.target[key]
    
#PassThroughDict - Dictionary that will __getitem__ the values of a different dict if they exist
#Finalization will join the two dicts, overwriting everything in self with keys from target
#This allows for values in one dict to be used if they exist in calculating new values (specifically in init())
#but to also allow the programmer to give a different value in place of these calculated values which will
#be applied in the finalization.
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
_prefs = PassThroughDict(userPrefs) #The final values for preferences that userPrefs will be joined over top of once an init() occurs
prefs = DummyReadOnlyDict(_prefs) #Where all API values are read from (if one is read, we trigger an init())

#GLOBAL DATA
_data = {}
data = DummyReadOnlyDict(_data) 
        
def updateUserPrefs(moreUserPrefs):
    """
    Overwrites global API prefs (only before init() is called)

    Takes a dict with key-value pairs representing the prefs to be overridden
    and the value to override with
    """
    
    #They can only update the preferences (or should only update them) when we haven't init'd
    if DummyReadOnlyDict.triggered:
        raise RuntimeError("NASS has already been inited. User preferences shouldn't be changed now")
    
    #Join the user prefs overwriting the default prefs
    userPrefs.update(moreUserPrefs)

def init():
    """
    Inits the global state of prefs and data

    Called automatically when either nassGlobal.prefs and nassGlobal.data is
    accessed. Calculates all default preferences, substituting those specified
    by the programmer in updateUserPrefs when necessary (stored in userPrefs dict)
    """

    #DEFAULT USER PREFERENCES
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
