class NASSStubData():
    """
    Represents kvs from a NASSDB, all combine later to form case
    
    Multiple stubs can be combined to house all data belonging to specific
    parts of a case. feedData() and feedStubData() were made for this
    """
    
    @staticmethod
    def getKVIdentTuple(year, dbType, kvs):
        ret = [year, kvs["PSU"], kvs["CASENO"]]
        if dbType == "VEH":
            ret.append(kvs["VEHNO"])
        if dbType == "OCC":
            ret.append(kvs["OCCNO"])
        return tuple(ret)
    
    def __init__(self, year, dbType, kvs):
        if not dbType in ["CASE", "VEH", "OCC"]:
            raise ValueError("Invalid database type given")
    
        self.year = year
        self.type = dbType #CASE, VEH, OCC
        self.kvs = kvs
        
        try:
            self.getIdentTuple()
        except KeyError:
            raise ValueError("Invalid kvs for database type")
    
    def getIdentTuple(self):
        """
        Tuple for identifying which case and sub data (vehicle and occupant) this stub belongs to
        """
        return NASSStubData.getKVIdentTuple(self.year, self.type, self.kvs)
    
    def __hash__(self):
        return self.getIdentTuple().__hash__()
        
    def __eq__(self, other):
        return isinstance(other, self.__class__) and self.__hash__() == other.__hash__()
    
    def __ne__(self, other):
        return not self.__eq__(other)
    
    def __getitem__(self, key):
        return self.kvs[key]
        
    def __setitem__(self, key, val):
        self.kvs[key] = val
    
    def toJSONHelper(self):
        tmpDict = self.kvs.copy()
        tmpDict["CASE_YEAR"] = self.year
        return tmpDict
    
    def copyEmpty(self, type):
        """
        Copies this object with only the kvs that identify it
        
        type identifies which level the identification data should be copied
        down to
        """
        #Which KVs to move from old to new
        newKVList = ["PSU", "CASENO"]
        if type == "VEH":
            newKVList.append("VEHNO")
        if type == "OCC":
            newKVList.append("OCCNO")
        #Try to copy all those kvs
        try:
            newKVs = {k: self.kvs[k] for k in newKVList}
        except KeyError:
            raise ValueError("Data stub does not support an identity of type " + type + " when it is of type " + self.type)
            
        return NASSStubData(self.year, type, newKVs)
    
    def feedStubData(self, stubData):
        self.feedData(stubData.year, stubData.type, stubData.kvs)
    
    def feedData(self, year, dbType, kvs):
        """
        Feed more data into this stub's kvs only if compatible source kvs
        """
        try:
            cmpTuple = NASSStubData.getKVIdentTuple(year, dbType, kvs)
        except KeyError:
            raise ValueError("Kvs passed is not compatible with this data stub")
        if cmpTuple != self.getIdentTuple():
            raise ValueError("Kvs passed is not compatible with this data stub")
            
        self.kvs.update(kvs)
         
class NASSCase():
    """
    Represents a NASSCase
    
    Combines many stub datas from a single case into one
    large case with many useful functions
    """

    def __init__(self, stubData):
        self.vehs = {}
    
        self.stubData = stubData.copyEmpty("CASE")
        self.feedStubData(stubData)
    
    #Cases are made unique by their year, psu, and number
    #This is all stored in the accompanying stubData
    def __hash__(self):
        return self.stubData.__hash__()
    
    def __eq__(self, other):
        return isinstance(other, self.__class__) and self.__hash__() == other.__hash__()
    
    def __ne__(self, other):
        return not self.__eq__(other)
        
    def __getitem__(self, key):
        if type(key) == int:
            for veh in self.vehs:
                if veh["VEHNO"] == str(key):
                    return veh
            raise IndexError("No vehicle with that VEHNO exists")
        elif key == "CASE_YEAR":
            return self.stubData.year
        else: # type(key) == str:
            return self.stubData[key]
        
    def __setitem__(self, key, val):
        if type(key) == int:
            raise ValueError("Cannot set an integer key on this object")
        elif key == "CASE_YEAR":
            self.stubData.year = val
        else: # type(key) == str:
            self.stubData[key] = val
    
    def __len__(self):
        return len(self.vehs.keys())
    
    def toJSONHelper(self):
        obj = self.stubData.toJSONHelper()
        obj["VEHICLES"] = [v.toJSONHelper() for v in self.vehs]
        return obj
    
    def matchesKVsIdent(self, year, kvs):
        return NASSStubData.getKVIdentTuple(year, "CASE", kvs) == self.stubData.getIdentTuple()
    
    def feedStubData(self, stubData):
        """
        Feeds stub data into the case
        """
        #If the stub data is a case, feed to this object's stubData
        if stubData.type == "CASE":
            self.stubData.feedStubData(stubData)
        #Otherwise it should be buried deeper in the case
        else:
            idTup = stubData.getIdentTuple()[:4]
            if not idTup in self.vehs:
                self.vehs[idTup] = NASSCaseVehicle(stubData)
            else:
                self.vehs[idTup].feedStubData(stubData)
    
    #TODO: Redo pretty print
    def prettyPrint(self, fixedLen=None):
        ret = "CASE: year:\"" + str(self["CASE_YEAR"]) + "\" psu:\"" + str(self["PSU"]) + "\" caseno:\"" + str(self["CASENO"]) + "\"\n"
        """for db, kvs in self.dbs.items():
            substr = "[" + str(db) + "| "
            for k, v in kvs.items():
                substr += str(k) + ":" + str(v) + ", "
                if len(substr) > 200:
                    s += substr + "\n"
                    substr = ""
            substr += "]\n"
        ret += substr"""
        return ret
        
class NASSCaseVehicle(NASSCase):
    """
    Represents a vehicle in a NASSCase
    """

    def __init__(self, stubData):
        self.occs = {}
    
        self.stubData = stubData.copyEmpty("VEH")
        self.feedStubData(stubData)
    
    def toJSONHelper(self):
        obj = self.stubData.toJSONHelper()
        obj["OCCUPANTS"] = [o.toJSONHelper() for o in self.occs]
        return obj
    
    def feedStubData(self, stubData):
        """
        Feeds stub data into the vehilce
        """
        #If the stub data is a vehicle, feed to this object's stubData
        if stubData.type == "VEH":
            self.stubData.feedStubData(stubData)
        #Otherwise it should be buried deeper in the vehicle (as an occupant)
        else:
            idTup = stubData.getIdentTuple()
            if not idTup in self.occs:
                self.occs[idTup] = NASSCaseOccupant(stubData)
            else:
                self.occs[idTup].feedStubData(stubData)
    
    def prettyPrint(self):
        raise NotImplementedError("Nope")
        

class NASSCaseOccupant(NASSCase):
    """
    Represents an occupant in a vehicle in a NASSCase
    """
    def __init__(self, stubData):
        self.stubData = stubData.copyEmpty("OCC")
        self.feedStubData(stubData)
    
    def toJSONHelper(self):
        return self.stubData.toJSONHelper()
    
    def feedStubData(self, stubData):
        """
        Feeds stub data into the occupant
        """
        #If the stub data is a vehicle, feed to this object's stubData
        if stubData.type == "OCC":
            self.stubData.feedStubData(stubData)
        else:
            raise ValueError("Not a valid stubData for an occupant")
    
    def prettyPrint(self):
        raise NotImplementedError("Nope")