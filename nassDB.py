import re

from sas7bdat import SAS7BDAT

from nassGlobal import prefs
from nassCase import NASSCase

class NASSDB():
    def __init__(self, data):
        self.valid = True
    
        self.data = data
        with SAS7BDAT(self.data["filePath"]) as db:
            self.columns = db.columns[:]
            #Decode some of the information
            for col in self.columns:
                col.name = col.name.decode(db.encoding, db.encoding_errors)
        
        #Set up mapping dictionaries
        self.colNameToIdx = {}
        for col in self.columns:
            self.colNameToIdx[col.name] = col.col_id
            
        if not "CASENO" in self.colNameToIdx:
            self.valid = False
            return
        
        '''#Special db properties
        #Long line support
        self.dbLongLine = None
        hasLINENO = False
        hasTEXTxx = False
        for col in self.columns:
            if col.name == "LINENO":
                hasLINENO = True
            elif re.match("^TEXT\d+$", col.name):
                hasTEXTxx = True
                self.dbLongLine = col.name
        
        if not (hasLINENO and hasTEXTxx):
            self.dbLongLine = None'''
        
        
        
        '''hasVEHNO = False
        hasOCCNO = False
        for col in self.columns:
            if col.name == "VEHNO":
                hasVEHNO = True
            elif col.name == "OCCNO":
                hasOCCNO = True
                
        #Database describes an occupant and must be linked as such
        elif hasVEHNO and hasOCCNO:
            self.dbType = "OCC"
        #Database describes a vehicle and must be linked as such
        elif hasVEHNO:
            self.dbtype = "VEH"'''
    
    #Gets a list of all the cases that match the search terms
    #Stubs - Should we return all the data we store in this database or just stubs of cases
    #Search - Search is a list of multiple terms that we test each row against for later final resolving of the cases and joins
    def getCases(self, stubs=False, search=None):
        if search:
            cases = {}
            for term in search:
                cases[term] = []
        else:
            cases = []
        with SAS7BDAT(self.data["filePath"], skip_header=True) as db:
            for row in db:
                #Take this row and make it a bunch of kvs
                #Also make the final case while we're at it
                kvs = {}
                case = NASSCase(self.data["year"])
                for col in self.columns:
                    kvs[col.name] = row[col.col_id]
                    
                    #If we only want case stubs skip everything else that's not in a case stub
                    if (not stubs) or col.name in prefs["stubKeys"]:
                        case.feedData(self.data["fileName"], {col.name:row[col.col_id]})
            
                #If we're searching, make sure this row matches
                if search:
                    for term in search:
                        if term.compare(kvs):
                            cases[term].append(case)
                else:
                    cases.append(case)
        
        return cases