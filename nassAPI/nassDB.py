import re

from .sas7bdatWrapper import SAS7BDATUtil

from .nassGlobal import prefs
from .nassCase import NASSStubData

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
            for p in os.path.split(splitPath):
                matchObj = re.match("^\d{4}$", splitPath[1])
                splitPath = splitPath[0]
                if splitPath == "":
                    raise ValueError("Could not infer the year from the given path")
            data["year"] = matchObj
        
        with SAS7BDATUtil(path) as db:
            #Store names in order of column id
            data["columnNames"] = db.column_names_decoded[:]
            
            if not "CASENO" in data["columnNames"]:
                raise RuntimeException(path + " is a SAS database but not a NASSDB database")
                
        
        
        if internal:
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
                data["TEXTxxNUM"] = matchObj.group(1)
                
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
            textxxRowCache = dict()
            toStubData = None
            for row in db:
                #Get the stubData for this row
                kvs = list(zip(db.column_names_decoded, row))
                
                #Can we use these kvs straight away?
                #TEXTxx has a much different case creation process (we wait until all lines of case are there)
                if "TEXTxx" in self.data:
                    #Check if the line we're looking for is already in the cache
                    ident = NASSStubData.getKVIdentTuple("", "CASE", row)
                    if ident in textxxRowCache:
                        cacheObj = textxxRowCache[ident]
                    else:
                        cacheObj = textxxRowCache[ident] = {
                            "lines" : dict(),
                            "lastLine" : -1,
                        }
                    #TODO: Make this more readable
                    
                    #Update lines
                    lineNum = int(row[db.colToIdx("LINENO")])
                    cacheObj["lines"][lineNum] = row[db.colToIdx(self.data["TEXTxx"])]
                    #Check to see if we found the last line, record if we did
                    
                    if len(row[db.colToIdx(self.data["TEXTxx"])]) < self.data["TEXTxxNUM"]:
                        cacheObj["lastLine"] = int(row[db.colToIdx(self.data["TEXTxx"])]
                        
                    #Check to see if we have all the lines, make the final kv if so
                    if cacheObj["lastLine"] == len(cacheObj["lines"].keys()):
                        #Combine all the lines into LINETXT
                        del row["LINENO"]
                        del row[self.data["TEXTxx"]]
                        row["LINETXT"] = "".join([cacheObj["lines"].values()]) #TODO: values might not be sorted!
                        toStubData = row
                        del textxxRowCache[ident]
                #If no TEXTxx, just straight to kvs
                else:
                    toStubData = kvs
                
                #Process the pending toStubData if we're able to
                if toStubData:
                    #Only use stubs keys if stubs
                    if stubs:
                        toStubData = {k:toStubData[k] for k in prefs["stubKeys"] if k in toStubData}
                    #Make the stub data
                    stubData = NASSStubData(self.data["year"], db.data["dbCaseType"], toStubData)
                    #Put in correct location
                    if search:
                        for term in search:
                            if term.compare(stubData.kvs):
                                matches[term].append(stubData)
                    else:
                        matches.append(stubData)
                    
                    toStubData = None
            
        return matches
    
    #Get all the stubDatas as cases
    def getCases(self, *args, **kwargs)
        stubDatas = self.getStubDatas(*args, **kwargs)
        return [NASSCase(sd) for sd in stubDatas]