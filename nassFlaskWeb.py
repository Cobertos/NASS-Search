import json

from flask import Flask
app = Flask("NASS")
app.debug = True

import nassGlobal
import nassSearchTerm

@app.route('/api_init')
def init():
    #SUPPORTED VALUES FOR OPTIONS
    supported = {}
    
    #DB related data
    supported["year"] = set()
    supported["dbName"] = set()
    supported["colName"] = {}
    #supported["searchValue"] = {"colName" : "searchValue"}
    for year, yearData in nassGlobal.data["preprocessDBInfo"].items():
        supported["year"].add(year)
        for db, dbData in yearData["dbs"].items():
            supported["dbName"].add(db)
            supported["colName"][db] = set()
            for col in dbData["columnNames"]:
                supported["colName"][db].add(col)
                #TODO: Add the searchValue stuff
    
    #Search related supports
    supported["join"] = [enumObj.name for enumObj in nassSearchTerm.NASSSearchJoin]
    supported["compareFunc"] = prefs["supportedCompareFuncs"].keys()
    supported["export"] = ["not", "currently", "implemented"]
    
    class SetEncoder(json.JSONEncoder):
        def default(self, obj):
            if isinstance(obj, set):
                return list(obj)
            return super().default(self, obj)
    
    return json.dumps(supported, cls=SetEncoder)
    
@app.route('/api_presearch')
def presearch():
    searchJSON = json.loads(flask.request.data)
    translateObj = {
        "dbName" : {dbData.prettyName : db for db, dbData in prefs["staticDBInfo"].dbs},
        "colName" : null,
        "searchValue" : null,
        "compareFunc" : prefs["supportedCompareFuncs"]
    }
    NASSSearchTerm.fromStrList(searchJSON, translateObj)
    
    #Do a presearch (compare everything to just the values of each DB and columns for each value)
    #Return alerts

    return 'Presearch'
    
@app.route('/api_search')
def search():
    return 'Search'
    
@app.route('/api_searchPoll')
def searchPoll():
    return 'Search Poll'

if __name__ == "__main__":
    app.run()