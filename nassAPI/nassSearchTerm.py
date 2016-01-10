import os
from enum import Enum

from .sas7bdatWrapper import SAS7BDATUtil
from .nassGlobal import prefs, data
from .nassDB import NASSDB

class NASSSearchJoin(Enum):
    AND = 0
    OR = 1
 
#A heirarchical node type object that holds all the parameters of a search
#Represents a search, holds not mutable state
#Contains two main fields:
# .terms are the terms used to search
# .inverse is a logical not of anything this specific term contains (think boolean logic)
class NASSSearchTerm():
    #Terms can be two things
    #1) A dict containing dbName, colName, searchValue, and compareFunc
    #2) An odd length tuple of (term, join, term, join, term ...)
    # In this tuple a term is anoter NASSSearchTerm. A join is a value of NASSSearchJoin enum
    def __init__(self, terms, inverse=False):
        self.terms = terms
        self.inverse = inverse
        self.errorCheck()
    
    def __str__(self):
        return self.toStrList().__str__()
    
    def __eq__(self, other):
        return self.__hash__() == other.__hash__()
        
    def __ne__(self, other):
        return not self.__eq__(other)
        
    def __hash__(self):
        if isinstance(self.terms, dict):
            return (frozenset(self.terms.items()), self.inverse).__hash__()
        elif isinstance(self.terms, tuple):
            return (self.terms, self.inverse).__hash__()
            
    #Error checks term and all subterms
    def errorCheck(self):
        terms = self.terms
        #Error check dictionary
        if isinstance(terms, dict):
            keys = terms.keys()
            if len(keys) != 4 or not ("dbName" in keys and "colName" in keys and "searchValue" in keys and "compareFunc" in keys):
                raise ValueError("Dictionary for search term did not contain the right terms")
        #Error check tuple
        elif isinstance(terms, tuple):
            if len(terms) == 0:
                raise ValueError("No search terms were given")
            if len(terms) == 1:
                raise ValueError("Only one search term given. Do not create tuples containing one term.")
            if len(terms) % 2 != 1:
                raise ValueError("Search must contain an odd number of terms")
            termCount = 0
            for term in terms:
                #Even Term
                if termCount % 2 == 0 and not isinstance(term, NASSSearchTerm):
                    raise ValueError("Even term was not a search term")
                #Odd Term
                elif termCount % 2 == 1 and not isinstance(term, NASSSearchJoin):
                    raise ValueError("Odd term was not a join term")
                #Recursive check
                if isinstance(term, NASSSearchTerm):
                    term.errorCheck()
                
                termCount += 1
        #Other types are not allowed
        else:
            raise ValueError("Terms was not a dict or a tuple")
    
    #Returns all the distinct (terms containing terms of just one DB) terms from a DB or dbName
    #Tries to keep large terms consisting of one DB together
    #This function is recursive
    def ofDB(self, dbName):
        #If it's just a dict term, it's simple
        if isinstance(self.terms, dict):
            if self.terms["dbName"] == dbName:
                return set([self])
            else:
                return set()
        
        #Tuple of terms is harder
        #Once we find any chunk that's not of the DB, this entire term becomes not a largeTerm.
        #If all the terms are of largeTerm, it returns itself (because it's all made up of the same DB)
        elif isinstance(self.terms, tuple):
            largeTerm = True 
            dbTerms = set()
            for term in self.terms:
                #Joiner
                if isinstance(term, NASSSearchJoin):
                    continue
                #More child terms    
                elif isinstance(term, NASSSearchTerm):
                    childTerms = term.ofDB(dbName)
                    #If the child term does not equal the returned set, it is 
                    if len(childTerms) != 1:
                        largeTerm = False
                        
                    dbTerms = dbTerms.union(childTerms)
                    continue
                
            if largeTerm:
                return set([self])
            else:
                return dbTerms
    
    #Compares a term to a list of kvs of colName->rowValue
    def compare(self, kvs):
        #Func for mapping of NASSSearchTerms to some other value
        def mapFunc(term):
            #Dict term can be compared
            if isinstance(term.terms, dict):
                if not term.terms["colName"] in kvs: #Column wasn't in the dict, wat?
                    raise ValueError("Term compared to kv that didn't contain column described in search (wrong DB row compared?)")
                value = kvs[term.terms["colName"]]
                return term.terms["compareFunc"](value, term.terms["searchValue"])
            #List terms need more work
            elif isinstance(term.terms, list):
                return term.resolve(mapFunc, joinFunc)
        
        #Func for joining mapped values based on a join
        def joinFunc(firstTerm, join, secondTerm):
            if join == NASSSearchJoin.AND:
                return firstTerm and secondTerm
            elif join == NASSSearchJoin.OR:
                return firstTerm or secondTerm

        finalMatch = self.resolve(mapFunc, joinFunc)
        
        #The '^' is XOR. Return finalMatch or inverse of it
        return self.inverse ^ finalMatch
    
    #Resolve this list to a single term based on a mapping of terms to values (mapFunc) and a description on how to join them (joinFunc)
    #Will not modify the object in any way and uses separate lists to keep track of the entire term (kind of how toStrList works) in local scope
    #This function is indirectly recursive in that the mapFunc usually calls resolve again to work on child terms of a large term
    def resolve(self, mapFunc, joinFunc):
        if isinstance(self.terms, dict):
            return mapFunc(self)
        elif isinstance(self.terms, tuple):
            #1)Replace each term with resolved term
            resolvedList = []
            for term in self.terms:
                if isinstance(term, NASSSearchJoin):
                    resolvedList.append(term)
                else:
                    resolvedList.append(mapFunc(term))
                
            #2)Perform the operations on the terms described by the logical joins
            #We made a list of [resolved, joiner, resolved, joiner, resolved ...]
            #Resolve the operators by precedence.
            newResolvedList = []
            lastJoin = None
            precedence = [(NASSSearchJoin.AND,), (NASSSearchJoin.OR,)]
            for ops in precedence:
                newResolvedList = []
                for resolvedTerm in resolvedList:
                    #Joiner
                    if isinstance(resolvedTerm, NASSSearchJoin):
                        #Store last join if it's in this precedence pass, otherwise append for later
                        if resolvedTerm in ops:
                            lastJoin = resolvedTerm
                        else:
                            newResolvedList.append(resolvedTerm)
                        continue
                    #resolvedTerm
                    else:
                        #If there's a lastJoin take the current term and compare to the last and put that on
                        if lastJoin != None:
                            #Append the result of firstTerm JOIN secondTerm where
                            #firstTerm is the previous term in the list
                            #JOIN is the lastJoin recorded (and not appended into the list)
                            #secondTerm is this currently held term
                            joinedTerm = joinFunc(newResolvedList.pop(), lastJoin, resolvedTerm)
                            newResolvedList.append(joinedTerm) 
                            lastJoin = None
                        #Otherwise just append
                        else:
                            newResolvedList.append(resolvedTerm)
                
                #At the end of an operator, set the new list to be the one resolved now
                resolvedList = newResolvedList
                
            return resolvedList[0]
    
    #Returns all the dicts from the entire NASSSearch term tree in one list
    def allTermDicts(self):
        return [s.terms for s in self._allTermDicts()]
    def _allTermDicts(self):
        if isinstance(self.terms, dict):
            return set([self])
        elif isinstance(self.terms, tuple):
            retObj = set()
            for term in self.terms:
                if not isinstance(term, NASSSearchTerm):
                    continue
                moreTerms = term._allTermDicts()
                retObj.update(moreTerms)
                    
            return retObj
    
    #Acts like a normal NASSSearchTerm without the class types
    #Has dicts, lists, etc, in places they'd normally be and strings become joins
    @classmethod
    def fromJSON(cls, jsonObj, translateObj=None):
        #Strings ==> Joins
        if isinstance(jsonObj, str):
            return NASSSearchJoin[jsonObj]
        #Dicts ==> Dict term (with translation)
        elif isinstance(jsonObj["terms"], dict):
            #See if we need to translate any dict terms
            if translateObj:
                for transKey, transDict in translateObj.items():
                    #Do we want to translate this term
                    if not transDict:
                        continue
                    
                    #Is this term in the dictionary
                    if not transKey in jsonObj["terms"]:
                        raise ValueError("No such property " + transKey + " on jsonObj")
                    
                    #Can't translate this value
                    if not jsonObj["terms"][transKey] in transDict.keys():
                        continue
                    
                    #Apply the translated value based on the dictionary
                    jsonObj["terms"][transKey] = transDict[jsonObj["terms"][transKey]]
                    
            return NASSSearchTerm(jsonObj["terms"], inverse=jsonObj["inverse"])
        #List ==> List term of all converted terms
        elif isinstance(jsonObj["terms"], list):
            arrObj = []
            for term in jsonObj["terms"]:
                arrObj.append(cls.fromJSON(term))
            
            return NASSSearchTerm(tuple(arrObj), inverse=jsonObj["inverse"])
    
    #Another import/export format for terms, this one specifically easy to write in python
    #Instead of forming a search term with dicts, tuples and the above classes, or JSON, a term can be formed from
    #1) A 4 or 5 tuple (["NOT"], dbName, colName, searchValue, compareFunc) for a single dict term
    #2) A list of the form [["NOT"], term, joinerString, term, joinerString, term ...] where terms are more 4/5 tuples or lists
    #The "NOT"s are optional in both cases to invert certain strings
    #JoinerString is a string representation of NASSSearchJoin
    @classmethod
    def fromStrList(cls, stringTerms, translateObj=None):
        inverse = False
        if stringTerms[0] == "NOT":
            inverse = True
            stringTerms = stringTerms[1:]
        
        #Single tuple term become dict terms
        if isinstance(stringTerms, tuple):
            dictTerm = {
                "dbName" : stringTerms[0],
                "colName" : stringTerms[1],
                "searchValue" : stringTerms[2],
                "compareFunc" : stringTerms[3]
            }
            return NASSSearchTerm(dictTerm, inverse=inverse)
        #Lists of multiple terms become tuple terms
        elif isinstance(stringTerms, list):
            terms = []
            for term in stringTerms:
                if isinstance(term, str):
                    terms.append(NASSSearchJoin[term])
                else:
                    terms.append(cls.fromStrList(term))
            return NASSSearchTerm(tuple(terms), inverse=inverse)
        
    def toStrList(self):
        if isinstance(self.terms, dict):
            out = (self.terms["dbName"],
                    self.terms["colName"],
                    self.terms["searchValue"],
                    self.terms["compareFunc"])
            if self.inverse:
                out = ("NOT",) + out
        elif isinstance(self.terms, tuple):
            out = ["NOT"] if self.inverse else []
            for term in self.terms:
                if isinstance(term, NASSSearchJoin):
                    termStr = str(term)
                    dotPos = termStr.find(".")
                    termEnd = termStr[dotPos+1:]
                    out.append(termEnd)
                else: #isinstance(term, NASSSearchTerm):
                    out.append(term.toStrList())
                    
        return out

#NASSSearch continues to collect data from each subsequent search and how it relates to the original terms and
#resolves it all down to the final cases        
class NASSSearch():
    def __init__(self, term):
        self.search = term
        self.foundCases = set()
    
    #Perform the search
    def perform(self):
        #Go through each year and each DB in that year
        print("Root is at " + prefs["rootPath"])
        for year, yearInfo in data["preprocessDBInfo"].items():
            termsToCases = {}
            for dbName, dbInfo in yearInfo["dbs"].items():
                #Relevant to search?
                relevantTerms = self.search.ofDB(dbName)
                if len(relevantTerms) == 0:
                    continue #Not a relevant database
                
                #Open the database and get cases
                dbInfo["filePath"] = os.path.join(prefs["rootPath"], dbInfo["filePath"])
                nassDB = NASSDB(dbInfo)
                staticDBInfo = data["staticDBInfo"]["dbs"][dbName]
                
                printStr = year + "  \"" + staticDBInfo["prettyName"] + "\" @ \"" + ((dbInfo["filePath"][:35] + '..') if len(dbInfo["filePath"]) > 35 else dbInfo["filePath"]) + "\""   
                print(printStr)
        
                cases = nassDB.getCases(stubs=True,search=relevantTerms)
                termsToCases.update(cases)
        
            self.foundCases = self.foundCases.union(self.resolve(termsToCases))
    
    #Take the collected termsToCases (terms from self.search mapped to datasets) and
    #compute the final dataset
    def resolve(self, termsToCases):        
        #Func for mapping of NASSSearchTerms to some other value
        def mapFunc(term):
            if not term in termsToCases:
                if isinstance(term.terms, dict):
                    #Woah, that's not good, we found a singular term that didn't match.
                    #It has no more children so it's not like it was a non-distinct term.
                    #We must be missing some data in the search.
                    raise RuntimeError("Term with no matching data in NASSSearch. Missed a DB query?\nOffending term:" + str(term))
                else:
                    #A term that wasn't found just may be non-distinct
                    return term.resolve(mapFunc, joinFunc)
            else:
                #The actual resolution
                return termsToCases[term]
        
        #Func for joining mapped values based on a join
        def joinFunc(firstTerm, join, secondTerm):
            if join == NASSSearchJoin.AND:
                return firstTerm.intersect(secondTerm)
            elif join == NASSSearchJoin.OR:
                return firstTerm.union(secondTerm)
                
        return self.search.resolve(mapFunc, joinFunc)
    
    def export(self, how):
        if how == "cases":
            return self.foundCases
        elif how == "fullCases":
            #Go back through all dbs and get everything
            raise NotImplementedError("Not implemented yet")
        elif how == "links":
            #First take all the cases and sort them by year
            casesByYear = {}
            for case in self.foundCases:
                if case.year in casesByYear:
                    casesByYear[case.year].append(case)
                else:
                    casesByYear[case.year] = [case]
        
            #Go through each year and compare the cases to get the link
            casesToLink = []
            for year in casesByYear.keys():
                with SAS7BDATUtil(data["preprocessDBInfo"][year]["linksDB"]) as linksDB:
                    for row in linksDB:
                        #Compare the row to the cases of that year
                        for case in casesByYear[year]:
                            if case.compare(linksDB.rowToKVs(row)):
                                print("FOUND")
                                which = "CASEID" if "CASEID" in linksDB.column_names_decoded else "SCASEID"
                                #caseid = '{:0f}'.format()
                                caseid = str(row[linksDB.colToIdx(which)]).rstrip("0").rstrip(".")
                                url = "http://www-nass.nhtsa.dot.gov/nass/cds/CaseForm.aspx?xsl=main.xsl&CaseID=" + caseid
                                casesToLink.append((case,url))
                                casesByYear[year].remove(case)
                                continue
                            
            return casesToLink #Returns a list of tuples
                    
            #Get the id
            #Create the links and output the cases
            raise NotImplementedError("Not implemented yet")
        elif how == "json":
            fullCases = self.export("fullCases")
            #Go through each case and output to json
            #Combine all the strings and return string
            raise NotImplementedError("Not implemented yet")
        elif how == "xls":
            fullCases = self.export("fullCases")
            #Go through each case and output to xls
            #Combine all strings into file
            raise NotImplementedError("Not implemented yet")