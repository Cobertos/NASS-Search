'''class SearchTerm():
    def __init__(self, dbName, colName, searchValue, compareFunc):
        self.dbName = dbName
        self.colName = colName
        self.searchValue = searchValue
        self.compareFunc = compareFunc
    
    def compare(self, value):
        return self.compareFunc(value, self.searchValue)

'''

'''print("Searching DBs")
    def matchIt(src, test):
        return test in src

    searchTerms = [
        SearchTerm("acc_desc", "TEXT71", "dog", matchIt),
        SearchTerm("typ_acc", "TEXT66", "dog", matchIt),
        SearchTerm("veh_pro", "TEXT81", "dog", matchIt),
        SearchTerm("pers_pro", "TEXT91", "dog", matchIt)
    ]

    matches = []
    for dbName, db in dbs.items():
        sts = []
        for st in searchTerms:
            if st.dbName == dbName:
                sts.append(st)
        
        if not sts:
            continue
        
        print("Searching: " + dbName)    
        matches += db.search(sts)

    print("Getting relevant records")
    rows = {}
    for dbName, db in dbs.items():
        print("Searching: " + dbName)
        kvs = db.getCaseIDs(matches)
        for kv in kvs:
            caseID = kv["CASEID"]
            if not caseID in rows:
                rows[caseID] = kv
            else:
                for kNew, vNew in kv.items():
                    if kNew in rows[caseID]:
                        if vNew and rows[caseID][kNew]:
                            rows[caseID][kNew] += vNew
                    else:
                        rows[caseID][kNew] = vNew
                #rows[caseID].update(kv)'''