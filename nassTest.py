#Unit testing?

#The main test function
#CaseTuples consist of 2 tuples of the form (case, expectSuccess)
#case is the object to test with testFunc
#expectSuccess is whether or not testFunc(case) will error. (So we can expect a test to fail and make that a success)
#testFunc is a function returning None on success or a reason in a string in a failure
def testCases(caseTuples, testFunc, useExpectSuccess=True):
    for case in caseTuples:
        if useExpectSuccess:
            expectSuccess = case[1]
            case = case[0]
        else:
            expectSuccess = True
        
        passed = False
        try:
            reason = testFunc(case)
            if not expectSuccess:
                reason = "No error occured"
            else:
                passed = True
        except Exception as e:
            if not expectSuccess:
                passed = True
            else:
                print("Failed on case: " + str(case))
                print("Reason: Unexpected exception")
                raise e
                
        try:
            assert passed
        except AssertionError as e:
            print("Failed on case: " + str(case))
            print("Reason: " + reason)
            raise e



#====Search Terms====
from nassSearchTerm import NASSSearchTerm, NASSSearch

#Search term string functions
def testStringStuff(obj):
    if not obj == NASSSearchTerm.fromStrList(obj).toStrList():
        return "In an out test failed | " + str(obj) + " did not equal " + str(NASSSearchTerm.fromStrList(obj).toStrList())
    if not obj.__str__() == NASSSearchTerm.fromStrList(obj).__str__():
        return "Strings did not match"
    return None

tuple = [
("db1", "bbb", "ccc", "ddd"),
("db2", "bbb", "ccc", "ddd"),
("db3", "bbb", "ccc", "ddd"),
("db1", "___", "ccc", "ddd"),
("db2", "___", "ccc", "ddd"),
("db3", "___", "ccc", "ddd")]

cases = [
#Single terms
( tuple[0], True   ),
( [tuple[1]], False ),
( ["aaa", "bbb", "ccc", "ddd"], False ),

#Multiple terms
( [tuple[0], "OR", tuple[3]], True ),
( [tuple[0], "AND", tuple[1], "AND", tuple[0]], True ),
( ["NOT", tuple[0], "AND", tuple[1]], True ),
( ["AND", "AND"], False ),
( ["AND", "AND", "AND"], False ),
( ["NOT", tuple[0], tuple[2]], False ),

#Nested terms
( [tuple[0], "AND", tuple[1], "OR", [tuple[0], "OR", tuple[2]]] , True )
]
    
testCases(cases, testStringStuff)


#ofDB
tmp1 = [("aaa", "bbb", "ccc", "ddd"), "OR", ("aaa", "bbb", "ccd", "ddd")]
tmp = ["NOT", ("aaa", "bbb", "ccc", "ddd"), "AND", ("aab", "bbb", "ccc", "ddd"), "AND", ("aaa", "bbb", "ccc", "ddd"), "OR", tmp1]
tmpTerm = NASSSearchTerm.fromStrList(tmp)
 
assert tmpTerm.ofDB("aaa") == set([NASSSearchTerm.fromStrList(tmp1)]) | set([NASSSearchTerm.fromStrList(("aaa", "bbb", "ccc", "ddd"))])

#resolve
'''from nassSearchTerm import NASSSearchJoin, resolveJoinedList
def testCompare(obj):
    def mapFunc(obj):
        return obj
    def joinFunc(firstTerm, join, secondTerm):
        if join == NASSSearchJoin.AND:
            return firstTerm and secondTerm
        elif join == NASSSearchJoin.OR:
            return firstTerm or secondTerm
    return None if resolveJoinedList(obj[0], resolveFunc, joinFunc) == obj[1] else "Did not match"

#Should return True because of operator precedence
assert testCompare(([True, NASSSearchJoin.OR, True, NASSSearchJoin.AND, False], True)) == None'''

#compare
def comp(found, find):
    return found == find
tmp = NASSSearchTerm.fromStrList([("aaa", "bbb", "ccc", comp), "AND", ("aaa", "___", "ccc", comp)])
def testCompare(obj):
    kvs = obj[0]
    expected = obj[1]
    if tmp.compare(kvs) != expected:
        return "Comparison to kvs was not " + expected + " as expected."
    return None
    
cases = [
({"bbb" : "ccc", "___" : "ccc"}, True),
({"bbb" : "ccc", "___" : "ccb"}, False),
({"bbb" : "ccb", "___" : "ccc"}, False)
]

testCases(cases, testCompare, useExpectSuccess=False)