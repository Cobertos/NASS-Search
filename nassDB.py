import re

from sas7bdat import SAS7BDAT


class NASSDBData():
    def __init__(self, filepath):
        self.filepath = filepath

class NASSDB():
    def __init__(self, data):
        self.valid = True
    
        self.data = data
        with SAS7BDAT(self.data.filepath) as db:
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
            
        #Determine if we need to do any special transformation on the database columns to get a full row for case
        self.dbType = "NORMAL"
        self.longTextName = ""
        
        hasLINENO = False
        hasTEXTxx = False
        hasVEHNO = False
        hasOCCNO = False
        for col in self.columns:
            if col.name == "LINENO":
                hasLINENO = True
            elif re.match("^TEXT\d+$", col.name):
                hasTEXTxx = True
                self.longTextName = col.name
            elif col.name == "VEHNO":
                hasVEHNO = True
            elif col.name == "OCCNO":
                hasOCCNO = True
                
        #Database contains a field that continues over multiple rows (a long string)        
        if hasLINENO and hasTEXTxx:
            self.dbType = "LTEXT"
        #Database describes an occupant and must be linked as such
        elif hasVEHNO and hasOCCNO:
            self.dbType = "OCC"
        #Database describes a vehicle and must be linked as such
        elif hasVEHNO:
            self.dbtype = "VEH"
    
    #Gets a list of all the cases that match the search terms
    def getCases(self, stubs=False, search=None):
        if search != None:
            print("Search is not implemented yet, will be ignored")
        
        stubKeys = ["CASENO", "PSU", "VEHNO", "OCCNO"]
            
        cases = {}
        with SAS7BDAT(self.data.filepath, skip_header=True) as db:
            for row in db:
                #Get the current case of this row
                rowCaseNO = row[self.colNameToIdx["CASENO"]]
                cases[rowCaseNO] = {}
                #For every column in this database, add a kv to the dictionary
                for col in self.columns:
                    #If we only want case stubs skip everything else that's not in a case stub
                    if stubs and not col.name in stubKeys:
                        continue
                    cases[rowCaseNO][col.name] = row[col.col_id]
        
        return cases
    
    #Searches the specific columns matches a specific value using a compare function all from searchTerms    
    '''def search(self, searchTerms):
        matches = []
        with SAS7BDAT(self.filepath, skip_header=True) as db:
            for row in db:
                for st in searchTerms:
                    idx = self.colNameToIdx[st.colName]
                    if st.compare(row[idx]):
                        matches.append(row[self.colNameToIdx["CASEID"]])
        return matches'''