import re

from .sas7bdatWrapper import SAS7BDATUtil

from .nassGlobal import prefs
from .nassCase import NASSCase

class NASSDB():
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
        if year:
            data["year"] = year
        else:
            #TODO:Split up path by / or \, get any folder that happens to be all numbers >= 4 digits
        
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
                    
            if TEXTxx != None and hasLINENO:
                #Long line columns exist
                data["TEXTxx"] = TEXTxx
                
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
                
            
#TODO: Change class name to NASSCaseDB
#TODO: Replace all uses of db.valid with a getData try/catch
#TODO: Change all constructors to use the filepath instead of the data object
#TODO: Search should be mandatory but allow wildcards (for getCases)
#TODO: self.data["year"] what do we do with that
#TODO: Add TEXTxx support
    def getInstanceData(self):
        """
        getData() but on an instance
        """
        return self.data

    def __init__(self, path, year=None):
        self.getData = self.getInstanceData
        self.data = data = self.__class__.getData(path, year=year, internal=True)
        
    #Gets a list of all the cases that match the search terms
    #Stubs - Should we return all the data we store in this database or just stubs of cases
    #Search - Search is a list of multiple terms that we test each row against. Each match is stored along with it's matching term
    #           No search is just a dump of all the cases in the file
    def getCases(self, stubs=False, search=None):
        if search:
            cases = {}
            for term in search:
                cases[term] = []
        else:
            cases = []
        
        def getIdent(self, db, row):
            if self.data["dbCaseType"] == "CASE":
                return row[db.colToIdx("CASENO")]
            elif self.data["dbCaseType"] == "OCC":
                return row[db.colToIdx("CASENO")] + "_" + row[db.colToIdx("VEHNO")]
            elif self.data["dbCaseType"] == "VEH":
                return row[db.colToIdx("CASENO")] + "_" + row[db.colToIdx("VEHNO")] + "_" + row[db.colToIdx("OCCNO")]
        
            
        with SAS7BDATUtil(self.data["filePath"], skip_header=True) as db:
            textxxRowCache = dict()
            for row in db:
                #TEXTxx has a much different case creation process (we wait until all lines of case are there)
                if "TEXTxx" in self.data:
                    ident = getIdent(self, db, row)
                    if ident in textxxRowCache:
                        cacheObj = textxxRowCache[ident]
                    else:
                        cacheObj = textxxRowCache[ident] = {
                            "lines" : dict(),
                            "lastLine" : -1,
                        }
                
                    lineNum = int(row[db.colToIdx("LINENO")])
                    cacheObj["lines"][lineNum] = row[db.colToIdx(self.data["TEXTxx"])]
                    if row[db.colToIdx(self.data["TEXTxx"])] < self.data["TEXTxxNUM"]:
                        cacheObj["lastLine"] = int(row[db.colToIdx(self.data["TEXTxx"])]
                        
                    if cacheObj["lastLine"] == len(cacheObj["lines"].keys()):
                        #TODO: Get the final case from these lines and compare
                
                
                #Take this row and make it a bunch of kvs
                kvs = zip(db.column_names_decoded, row)
                
                #Make the
                case = NASSCase(self.data["year"])
                for col in self.columns:
                    #If we only want case stubs skip everything else that's not in a case stub
                    if (not stubs) or col.name in prefs["stubKeys"]:
                        case.feedData(self.data["fileName"], {col.name:row[col.col_id]})
                
                case = None
                if search:
                    for term in search:
                        if term.compare(kvs):
                            cases[term].append(case)
                
                
            
                #If we're searching, make sure this row matches
                
                    
                else:
                    cases.append(case)
        
        return cases