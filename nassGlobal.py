prefs = {}
#Root folder to search
prefs["rootPath"] = "./nassDB"
#Directories that we're looking for in the nassDB folder
prefs["dataDirNames"] = ["ASCII", "Formatted Data", "Expanded SAS"]
#Keys kept for stub cases
prefs["stubKeys"] = ["CASENO", "PSU", "VEHNO", "OCCNO"]

data = {}

fstaticDBInfo = open("staticDBInfo.json", "r")
data["staticDBInfo"] = json.loads(fstaticDBInfo.read())