from enum import Enum

#Each term is a dictionary with dbName, colName, searchValue, compareFunc

class NASSSearchJoin(Enum):
    AND = 0
    OR = 1

class NASSSearchTerm():
    #Instead of forming a search term from all the classes a list of the form given below can be used
    #[term, joinerString, term, joinerString, term ...]
    #A term can either be a 4 tuple (dbName, colName, searchValue, compareFunc) or a list of the same format
    #JoinerString is a string from the NASSSearchJoin
    @classmethod
    def fromStrList(cls, stringTerms):
        terms = []
        for term in stringTerms:
            if isinstance(term, str):
                terms.append(NASSSearchJoin[term])
            elif isinstance(term, tuple):
                dictTerm = {
                    "dbName" : term[0],
                    "colName" : term[1],
                    "searchValue" : term[2],
                    "compareFunc" : term[3]
                }
                terms.append(NASSSearchTerm(dictTerm)
            else:
                terms.append(cls.fromStrList(listTerm))
        return NASSSearchTerm(terms)


    #Terms can be two things
    #1) Terms can either be a dict containing dbName, colName, searchValue, and compareFunc
    #2) Terms is an odd length list of [term, join, term, join, term ...]
    # In this list a term is anoter NASSSearchTerm. A join is a value of NASSSearchJoin enum
    def __init__(self, terms, inverse=False):
        #Error check dictionary
        if isinstance(terms, dict)
            keys = dict.keys()
            if len(keys) != 4 or not ("dbName" in keys and "colName" in keys and "searchValue" in keys and "compareFunc" in keys):
                raise ValueError("Dictionary for search term did not contain the right terms")
        #Error check list
        elif isinstance(terms, list):
            if len(terms) == 0:
                raise ValueError("No search terms were given")
            if len(terms) % 2 != 1:
                raise ValueError("Search must contain an odd number of terms")
            termCount = 0
            for term in terms:
                #Even Term
                if termCount % 2 == 0 and not isinstance(term, NASSSeachTerm):
                    raise ValueError("Even term was not a search term")
                #Odd Term
                elif not isinstance(term, NASSSeachJoin):
                    raise ValueError("Odd term was not a join term")
                
                termCount += 1
        #Other types are not allowed
        else:
            raise ValueError("Terms was not a dict or a list")
            
        self.terms = terms
        self.inverse = inverse
    
    #Returns all the terms of a given DB
    #Tries to keep large terms consisting of one DB together
    #This function is recursive
    def ofDB(self, dbName):
        #If it's just a dict term, it's simple
        if isinstance(self.terms, dict):
            if self.terms["dbName"] == dbName:
                return [self]
            else:
                return []
        
        #List of terms is harder
        #Once we find any chunk that's not of the DB, this entire term becomes not a largeTerm.
        #If all the terms are of largeTerm, it returns itself (because it's all made up of the same DB)
        largeTerm = True 
        dbTerms = []
        for term in self.terms:
            #Joiner
            if isinstance(term, NASSSearchJoin):
                continue
            #More child terms    
            elif isinstance(term, NASSSearchTerm):
                childTerms = term.ofDB(dbName)
                #If it returns one term, it's possible to continue the chain, otherwise just add them to the dbTerms
                #Zero denotes a term with no portions of this DB, so it breaks the chain too
                if len(largeTerm) != 1:
                    largeTerm = False
                    
                dbTerms.extend(childTerms)
                continue
            
        if largeTerm:
            return self
        else:
            return dbTerms
    
    #Compares a term to a list of kvs of colName->rowValue
    def compare(self, kvs):
        finalMatch = False
    
        #Dict term
        if isinstance(self.terms, dict):
            if not self.terms["colName"] in kvs: #Column wasn't in the dict, wat?
                raise ValueError("Term compared to kv that didn't contain column described in search (wrong DB row compared?)")
            value = kvs[self.terms["colName"]]
            finalMatch = self.terms["compareFunc"](value, self.terms["searchValue"]))
        #List term
        else:
            #Resolve all terms to bools in the list
            matchList = []
            for term in self.terms:
                #Joiner
                if isinstance(term, NASSSearchJoin):
                    matchList.append(term)
                    continue
                #More child terms
                elif isinstance(term, NASSSearchTerm):
                    matchList.append(term.compare(kvs))
                    continue

            #We made a list of [bool, joiner, bool, joiner, bool ...]
            #Resolve the operators by precedence. The actual joiner code is here which is a little weird but fine for now
            newMatchList = []
            lastJoin = None
            precendence = [(NASSSearchJoin.AND), (NASSSearchJoin.OR)]
            for ops in precedence:
                newMatchList = []
                for matchTerm in matchList:
                    #Joiner
                    if isinstance(matchTerm, NASSSearchJoin):
                        #Store last join if it's in this precedence pass, otherwise append for later
                        if matchTerm in ops:
                            lastJoin = matchTerm
                        else:
                            newMatchList.append(matchTerm)
                        continue
                    #bool
                    else:
                        #If there's a lastJoin take the current bool and compare to the last and put that on
                        if lastJoin != None:
                            if lastJoin == NASSSearchJoin.AND:
                                newMatchList.append(newMatchList.pop() and matchTerm)
                            elif lastJoin == NASSSearchJoin.OR:
                                newMatchList.append(newMatchList.pop() or matchTerm)
                            lastJoin = None
                        #Otherwise just append
                        else:
                            newMatchList.append(matchTerm)
                
                #At the end of an operator, set the new list to be the one resolved now
                matchList = newMatchList
                
            finalMatch = matchList[0]
        
        #The '^' is XOR. Return finalMatch or inverse of it
        return self.inverse ^ finalMatch
        
class NASSSearch():
    def __init__(self, term):
        self.search = term
    
    
        