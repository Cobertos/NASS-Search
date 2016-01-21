import re
import os

from .sas7bdatWrapper import SAS7BDATUtil

from .nassGlobal import prefs
from .nassCase import NASSStubData, NASSCase

class NASSCaseDB():
    """
    A NASS DB that holds case information
    
    * Performs automatic joining of long text lines (dbs with LINENO and TEXT## show just a LINETXT column)
    * Knows what level of case data the data in the db represents (case, vehicle, occupant)
    
    """

    @classmethod
    def getData(cls, path, year=None, internal=False):
        """
        Get the all the data about a case database
        
        Some of this is useful to outsiders (for example, in designing a GUI
        to know what is available to search over) while some of it is more
        internal. Set internal to True to get the internal data as well
        
        Year is the year this db belongs to. This will be inferred from the 
        path if None.
        """
        
        data = dict()
        data["filePath"] = path
        data["fileName"] = os.path.split(path)[1]
        if year:
            data["year"] = year
        else:
            splitPath = path
            while splitPath != "":
                splitPath = os.path.split(splitPath)
                
                matchObj = re.match("^(\d{4})$", splitPath[1])
                if matchObj:
                    data["year"] = matchObj.group(1)
                    break
                    
                splitPath = splitPath[0]
            if not "year" in data:
                raise ValueError("Could not infer the year from the given path")
        
        with SAS7BDATUtil(path) as db:
            #Store names in order of column id
            data["columnNames"] = db.column_names_decoded[:]
            
            if not "CASENO" in data["columnNames"]:
                raise RuntimeException(path + " is a SAS database but not a NASSDB database")
                
        #Check for long line columns
        hasLINENO = "LINENO" in data["columnNames"]
        TEXTxx = None
        for col in data["columnNames"]:
            if re.match("^TEXT\d+$", col):
                TEXTxx = col
                break
                
        if TEXTxx != None and hasLINENO:
            #Long line columns exist
            data["TEXTxx"] = TEXTxx
            matchObj = re.match("^TEXT(\d+)$", TEXTxx)
            data["TEXTxxNUM"] = int(matchObj.group(1))
            
            data["columnNames"].remove("LINENO")
            data["columnNames"].remove(TEXTxx)
            data["columnNames"].append("LINETXT")
        
        #Get the type of case database
        hasVEHNO = "VEHNO" in data["columnNames"]
        hasOCCNO = "OCCNO" in data["columnNames"]
        
        data["dbCaseType"] = "CASE"
        if hasVEHNO and hasOCCNO:
            data["dbCaseType"] = "OCC"
        elif hasVEHNO:
            data["dbCaseType"] = "VEH"
        
        #Cleanup if we don't want internal things
        if not internal:
            if "TEXTxx" in data:
                del data["TEXTxx"]
                del data["TEXTxxNUM"]
        
        return data
                
            
#TODO: Search should be mandatory but allow wildcards (for getCases)
    def getInstanceData(self):
        """
        getData() but on an instance
        """
        return self.data

    def __init__(self, path, year=None):
        self.getData = self.getInstanceData
        self.data = data = self.__class__.getData(path, year=year, internal=True)
    
    #Gets a list of all the stubDatas that match the search terms
    #Stubs - Should we return all the data we store in this database or just keys to identify the cases
    #Search - Search is a list of multiple terms that we test each row against. Each match is stored along with it's matching term
    #           No search is just a dump of all the matches in the file
    def getStubDatas(self, stubs=False, search=None):
        if search:
            matches = {}
            for term in search:
                matches[term] = []
        else:
            matches = []

        with SAS7BDATUtil(self.data["filePath"], skip_header=True) as db:
            textxxRowCache = {
                "lastIdent" : None,
                "lastKVs" : None,
                "lines" : dict()
            }
            toStubData = None
            for row in db:
                #Get the stubData for this row
                kvs = dict(zip(db.column_names_decoded, row))
                
                #Can we use these kvs straight away?
                #TEXTxx has a much different case creation process (we wait until all lines of case are there)
                if "TEXTxx" in self.data:
                    #Check if the line we're looking for is already in the cache
                    ident = NASSStubData.getKVIdentTuple("", "CASE", kvs)
                    
                    #If we started reading from a new ident, box up the old one, clear cache
                    if textxxRowCache["lastIdent"] and textxxRowCache["lastIdent"] != ident:
                        #Combine all the lines into LINETXT
                        del textxxRowCache["lastKVs"]["LINENO"]
                        del textxxRowCache["lastKVs"][self.data["TEXTxx"]]
                        
                        #Convert lines' keys to ints and sort by key
                        lineTuples = list(textxxRowCache["lines"].items())      #Get line tuples
                        lineTuples.sort(key=lambda itm: itm[0])                 #Sort by the key
                        lines = [t[1] for t in lineTuples]                      #Get just the lines
                        textxxRowCache["lastKVs"]["LINETXT"] = " ".join(lines)  #Join them all together

                        toStubData = textxxRowCache["lastKVs"]
                        #Back to none
                        textxxRowCache["lastIdent"] = None
                        textxxRowCache["lastKVs"] = None
                        textxxRowCache["lines"] = dict()
                        
                    #New one (also captures current line if last one boxed up)
                    if not textxxRowCache["lastIdent"]:
                        textxxRowCache["lastIdent"] = ident
                        textxxRowCache["lastKVs"] = kvs

                    #Update lines
                    lineNum = int(kvs["LINENO"])
                    textxxRowCache["lines"][lineNum] = kvs[self.data["TEXTxx"]]
                        
                #If no TEXTxx, just straight to kvs
                else:
                    toStubData = kvs
                
                #Process the pending toStubData if we're able to
                if toStubData:
                    #Only use stubs keys if stubs
                    if stubs:
                        initStubData = {k:toStubData[k] for k in prefs["stubKeys"] if k in toStubData}
                    #Make the stub data
                    stubData = NASSStubData(self.data["year"], self.data["dbCaseType"], toStubData)
                    #Put in correct location
                    if search:
                        for term in search:
                            if term.compare(toStubData):
                                matches[term].append(stubData)
                    else:
                        matches.append(stubData)
                    
                    toStubData = None
            
        return matches
    
    #Get all the stubDatas as cases
    def getCases(self, *args, **kwargs):
        stubDatas = self.getStubDatas(*args, **kwargs)
        if "search" in kwargs.keys():
            for k, v in stubDatas.items():
                stubDatas[k] = [NASSCase(sd) for sd in v]
            return stubDatas
        else:
            return [NASSCase(sd) for sd in stubDatas]