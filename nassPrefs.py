import os.path

from nassAPI.nassGlobal import init

#This file must be imported into any file that wants to use the API
#It will init the NASS API with all preferences the user wants

#User preferences
userPrefs = {}
#For prefs you can add, see nassAPI/nassGlobal.py, the prefs variable

#Init NASS
#Will throw RuntimeErrors if you didn't do the setup properly
init(userPrefs)
    