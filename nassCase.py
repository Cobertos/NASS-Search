from enum import Enum


#Defines a case from NASS

class NassCaseDataType(Enum):
    accident = 0
    vehicle = 1
    occupant = 2

class NassCase():
    def __init__(self):
        self.kvs = {}
        self.vehicles = {}
        self.occupants = {}
    
    def feedData(self, kvs, type):
        if type == NassCaseDataType.accident:
            self.kvs.update(kvs)
            return
        if type == NassCaseDataType.vehicle and "VEHNO" in kvs:
            vehno = kvs["VEHNO"]
            if vehno in self.vehicles:
                self.vehicles[vehno].update(kvs)
            else:
                self.vehicles[vehno] = kvs
            return
        if type == NassCaseDataType.occupant and "OCCNO" in kvs:
            occno = kvs["OCCNO"]
            if occno in self.vehicles:
                self.occupants[occno].update(kvs)
            else:
                self.occupants[occno] = kvs
            return
            
        print("Data could not be added to case")