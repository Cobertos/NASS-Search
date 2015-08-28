from enum import Enum


#Defines a case from NASS

class NASSCaseDataType(Enum):
    accident = 0
    vehicle = 1
    occupant = 2

class NASSCase():
    def __init__(self, year):
        self.year = None
        self.dbs = {}
        self.kvs = {}
        self.vehicles = {}
        self.occupants = {}
        self.isStub = False
    
    def __eq__(self, other):
        return self.dbs == other.dbs and self.year == other.year
    
    def __ne__(self, other):
        return not self.__eq__(other)
    
    def feedData(self, dbFrom, kvs):
        if dbFrom in self.dbs:
            self.dbs[dbFrom].update(kvs)
        else:
            self.dbs[dbFrom] = kvs
    
    
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