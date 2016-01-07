import traceback
import unittest


#nassDB.py - Loading a nass database with extra functionality


#nassSearchTerm.py - All the search term stuff
from nassAPI.nassSearchTerm import NASSSearchTerm, NASSSearch, NASSSearchJoin
class TestCase_NASSSearchTerm(unittest.TestCase):
    def setUp(self):
        self.ts = [ #Array of tuples to more easily create string lists
        ("db1", "bbb", "ccc", "ddd"),
        ("db2", "bbb", "ccc", "ddd"),
        ("db3", "bbb", "ccc", "ddd"),
        ("db1", "___", "ccc", "ddd"),
        ("db2", "___", "ccc", "ddd"),
        ("db3", "___", "ccc", "ddd")]
        
    
    def test_ValidTerms(self):
        strLists = [
        #Single term
        self.ts[0],
        #Multiple terms
        [self.ts[0], "OR", self.ts[3]],
        ["NOT", self.ts[0], "AND", self.ts[1]],
        #Nested terms
        ["NOT", self.ts[0], "AND", self.ts[1], "OR", [self.ts[0], "OR", self.ts[2]]],
        ]
    
        #All lists should succeed
        for strList in strLists:
            outStr = None
            try:
                term = NASSSearchTerm.fromStrList(strList)
            except Exception as e:
                outStr = ("Extended Exception (see below)\n\n" + traceback.format_exc() +
                    "\n" + str(strList) + " was invalid and should have been valid")
            if outStr:
                self.fail(msg=outStr)
            
            #Also, check the conversion: NASSSearchTerm <=> String List
            self.assertTrue(strList == term.toStrList(), "\n" + str(strList) + " != " + str(term.toStrList()))
    
    def test_InvalidTerms(self):
        strLists = [
        #Single term
        None, #Empty terms are invalid
        [],
        [self.ts[1]], #Don't accept collected terms with just one item
        ["aaa", "bbb", "ccc", "ddd"], #A tuple term that should be a list
        #Multiple terms
        ["AND", "AND"], #Not even
        ["AND", "AND", "AND"], #Not of form (NOT,), term, join, term
        ["NOT", self.ts[0], self.ts[2]], #Same as above
        ]
    
        #All lists should fail
        for strList in strLists:
            with self.assertRaises(Exception):
                term = NASSSearchTerm.fromStrList(caseStrList, msg=str(strList) + " was valid and should have been valid")
    
    def test_TermOfDB(self):
        #If we ofDB for db1...
        strList = [
        self.ts[0], "AND", self.ts[1], "AND", self.ts[2], "AND", #... in this row just self.ts[0]
        self.ts[3], "AND", self.ts[4], "AND", self.ts[5], "AND", #... in this row just self.ts[3]
        [self.ts[0], "AND", self.ts[3]]                          #... lastly, the entire chunk self.ts[0] and self.ts[3] will come out
        ]
        
        outStrLists = [self.ts[0], self.ts[3], [self.ts[0], "AND", self.ts[3]]]
        outTerms = [NASSSearchTerm.fromStrList(sl) for sl in outStrLists]
        
        term = NASSSearchTerm.fromStrList(strList)
        
        #Finds all sections of the term that specify a given db
        ofDBSet = term.ofDB("db1")
        
        self.assertTrue(ofDBSet == set(outTerms))
    
    def test_TermResolve(self):
        #Tests the resolve function of terms
        #Workhorse for resolving term trees in compare and other situations
        nts = [NASSSearchTerm.fromStrList(ts) for ts in self.ts] #Create terms from all tuples
        
        def mapFunc(obj):
            if isinstance(obj.terms, dict):
                if obj == nts[0]:
                    return True
                elif obj == nts[1]:
                    return False
            elif isinstance(obj.terms, tuple): #Resolve tuple terms by recursion, like most mapFuncs
                return obj.resolve(mapFunc, joinFunc)
        def joinFunc(firstTerm, join, secondTerm):
            if join == NASSSearchJoin.AND:
                return firstTerm and secondTerm
            elif join == NASSSearchJoin.OR:
                return firstTerm or secondTerm
                
        #Simple testing strList function, calls resolve
        def t(strList):
            term = NASSSearchTerm.fromStrList(strList)
            return term.resolve(mapFunc, joinFunc)
        
        #ts[0] becomes True, ts[1] becomes False
        #Simple test, no recursion
        self.assertTrue(t([self.ts[0], "OR", self.ts[1]]) == True)
        self.assertTrue(t([self.ts[0], "AND", self.ts[1]]) == False)
        
        #Will test the operator precendence
        self.assertTrue(t([self.ts[0], "OR", self.ts[0], "AND", self.ts[1]]) == True)
        
        #Test tuple terms, and operator precedence
        self.assertTrue(t([self.ts[0], "OR", self.ts[0], "AND", [self.ts[1], "AND", self.ts[0]]]) == True)
        
    """def test_CaseCompare(self):
        strList = [
        self.ts[0], "AND", self.ts[1], "AND", self.ts[2], "AND",
        self.ts[3], "AND", self.ts[4], "AND", self.ts[5]
        ]
    
        term = NASSSearchTerm.fromStrList(strList)
        
        #"resolves" the tree with booleans based on kvs where a term matchs
        case.compare({"""
        
    
    def test_CaseResolve(self):
    
    def test_DictTerms(self):
    
    def test_CaseFromJSON(self):


#compare
"""def comp(found, find):
    return found == find
tmp = NASSSearchTerm.fromStrList([("aaa", "bbb", "ccc", comp), "AND", ("aaa", "___", "ccc", comp)])
def testCompare(obj):
    kvs = obj[0]
    expected = obj[1]
    if tmp.compare(kvs) != expected:
        return "Comparison to kvs was not " + expected + " as expected."
    return None"""
if __name__ == "__main__":
    unittest.main()