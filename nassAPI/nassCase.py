from enum import Enum


#Defines a case from NASS

class NASSCaseDataType(Enum):
    accident = 0
    vehicle = 1
    occupant = 2

class NASSCase():
    def __init__(self, year):
        self.year = year
        self.psu = None
        self.num = None
        self.dbs = {}
        self.isValid = False
    
    #Cases are made unique by their year, psu, and number
    #There is much other data associated with cases but these make it unique
    #Once we get these we know exactly which case it is but it might not have all the data
    def __hash__(self):
        return (self.year, self.psu, self.num).__hash__()
    
    def __eq__(self, other):
        return self.__hash__() == other.__hash__()
        #return type(self) == type(other) and self.dbs == other.dbs and self.year == other.year
    
    def __ne__(self, other):
        return not self.__eq__(other)
    
    def feedData(self, dbFrom, kvs):
        #First add the data into dbs
        if dbFrom in self.dbs:
            self.dbs[dbFrom].update(kvs)
        else:
            self.dbs[dbFrom] = kvs
            
        #Check to see if we have a definitive psu and num
        if "PSU" in self.dbs[dbFrom]:
            self.psu = self.dbs[dbFrom]["PSU"]
        elif "CASENO" in self.dbs[dbFrom]:
            self.num = self.dbs[dbFrom]["CASENO"]
        
        if self.year and self.psu and self.num:
            self.isValid = True
            
    def compare(self, rowKVs):
        testKeys = ["PSU", "CASENO"]
        for dbKVs in self.dbs.values():
            for k in testKeys[:]:
                if k in dbKVs and k in rowKVs and rowKVs[k] == dbKVs[k]:
                    testKeys.remove(k)
                    
                if len(testKeys) == 0:
                    return len(testKeys) == 0
                
        return len(testKeys) == 0
    
    def prettyPrint(self, fixedLen=None):
        ret = "CASE: year:\"" + str(self.year) + "\" psu:\"" + str(self.psu) + "\" caseno:\"" + str(self.num) + "\"\n"
        for db, kvs in self.dbs.items():
            substr = "[" + str(db) + "| "
            for k, v in kvs.items():
                substr += str(k) + ":" + str(v) + ", "
                if len(substr) > 200:
                    s += substr + "\n"
                    substr = ""
            substr += "]\n"
        ret += substr
        return ret
    
    
        '''if type == NASSCaseDataType.accident:
            self.kvs.update(kvs)
            return
        if type == NASSCaseDataType.vehicle and "VEHNO" in kvs:
            vehno = kvs["VEHNO"]
            if vehno in self.vehicles:
                self.vehicles[vehno].update(kvs)
            else:
                self.vehicles[vehno] = kvs
            return
        if type == NASSCaseDataType.occupant and "OCCNO" in kvs:
            occno = kvs["OCCNO"]
            if occno in self.vehicles:
                self.occupants[occno].update(kvs)
            else:
                self.occupants[occno] = kvs
            return
            
        print("Data could not be added to case")'''