import traceback
import unittest


#nassDB.py - Loading a nass database with extra functionality
'''from nassAPI.nassDB import NASSDB
class TestCase_NASSDB(unittest.TestCase):
    def setUp(self):
        pass
        
    def test_Basics(self):'''
        

#nassSearchTerm.py - All the search term stuff
from nassAPI.nassSearchTerm import NASSSearchTerm, NASSSearch, NASSSearchJoin
class TestCase_NASSSearchTerm(unittest.TestCase):
    def setUp(self):
        def myEq(obj1, obj2):
            return obj1 == obj2
        def myStrIn(obj1, obj2):
            return obj1 in obj2
    
        #Array of tuples to more easily create string lists
        self.ts = [ 
        ("db_1", "col_1", "val", myEq),
        ("db_2", "col_1", "val", myEq),
        ("db_3", "col_1", "val", myStrIn),
        ("db_1", "col_2", "val", myEq),
        ("db_2", "col_2", "val", myEq),
        ("db_3", "col_2", "val", myStrIn)]
        
    
    def test_ValidTerms(self):
        strLists = [
        #Single term
        self.ts[0],
        ("NOT",) + self.ts[0][:],
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
            except ValueError as e:
                outStr = ("Extended Exception (see below)\n\n" + traceback.format_exc() +
                    "\n" + str(strList) + " was invalid and should have been valid")
            if outStr:
                self.fail(msg=outStr)
            
            #Also, check the conversion: NASSSearchTerm <=> String List
            self.assertEqual(strList, term.toStrList())
    
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
            with self.assertRaises(Exception, msg=str(strList) + " was valid and should have been valid"):
                term = NASSSearchTerm.fromStrList(caseStrList)
    
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
        ofDBSet = term.ofDB("db_1")
        
        self.assertEqual(ofDBSet, set(outTerms))
    
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
        self.assertEqual(t([self.ts[0], "OR", self.ts[1]]), True)
        self.assertEqual(t([self.ts[0], "AND", self.ts[1]]), False)
        
        #Will test the operator precendence
        self.assertEqual(t([self.ts[0], "OR", self.ts[0], "AND", self.ts[1]]), True)
        
        #Test tuple terms, and operator precedence
        self.assertEqual(t([self.ts[0], "OR", self.ts[0], "AND", [self.ts[1], "AND", self.ts[0]]]), True)
        
    def test_CaseCompare(self):
        #Just db1
        strList = [self.ts[0], "AND", self.ts[3]]
        term = NASSSearchTerm.fromStrList(strList)
        
        self.assertFalse(term.compare({
            "col_1" : "aaa", #Doesn't match anything
            "col_2" : "bbb",
            "col_3" : "ccc"
        }))
        self.assertFalse(term.compare({
            "col_1" : "val", #Only matches one column
            "col_2" : "bbb",
            "col_3" : "ccc"
        }))
        self.assertTrue(term.compare({
            "col_1" : "val", #Matches necessary columns
            "col_2" : "val",
            "col_3" : "ccc"
        }))
        
    def test_DictTerms(self):
        #Get all distinct dicts terms out of a term
        strList = [
        self.ts[0], "AND", [self.ts[1], "AND", self.ts[2]], "AND",
        self.ts[3], "AND", self.ts[4], "AND", self.ts[5], "AND", self.ts[0]
        ]
        dictTerms = NASSSearchTerm.fromStrList(strList).allTermDicts()
        compareTo = [NASSSearchTerm.fromStrList(strList).terms for strList in self.ts[:6]]
        
        self.assertCountEqual(dictTerms, compareTo)
        
    def test_CaseFromJSON(self):
        #Take JSON and create a term from it
        
        #Simple (one term)
        myJson = {
            "terms" : {
                "dbName" : "db_1",
                "colName" : "col_1",
                "searchValue" : "val",
                "compareFunc" : "something"
            },
            "inverse" : False
        }
        myStrList = ("db_1", "col_1", "val", "something")
        self.assertEqual(NASSSearchTerm.fromStrList(myStrList), NASSSearchTerm.fromJSON(myJson))
        
        #Complex (multiple terms)
        myJson = { "terms" : 
        [{
            "terms" : {
                "dbName" : "db_1",
                "colName" : "col_1",
                "searchValue" : "val",
                "compareFunc" : "something"
            },
            "inverse" : False
        },
        "AND",
        {
            "terms" : {
                "dbName" : "db_2",
                "colName" : "col_1",
                "searchValue" : "val",
                "compareFunc" : "something"
            },
            "inverse" : False
        }],
        "inverse" : False}
        myStrList = [("db_1", "col_1", "val", "something"), "AND", ("db_2", "col_1", "val", "something")]
        self.assertEqual(NASSSearchTerm.fromStrList(myStrList), NASSSearchTerm.fromJSON(myJson))
        
        
        
        
if __name__ == "__main__":
    unittest.main()