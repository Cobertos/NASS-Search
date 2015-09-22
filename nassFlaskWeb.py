import json
import os
import mimetypes
   
from flask import Flask, url_for, redirect
app = Flask("NASS")
app.debug = True

import nassGlobal
import nassSearchTerm

@app.route('/app/<path:file>')
def serve(file):
    path = "./webGui/" + file
    if(os.path.isfile(path)):
        resp = app.make_response(open(path, "rb").read())
        resp.mimetype = mimetypes.guess_type(file)[0]
        return resp
    else:
        abort(404)

@app.route('/')
def root():
    return redirect(url_for("serve",file="nassSearchUI.html"), 302)

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
    supported["compareFunc"] = list(nassGlobal.prefs["supportedCompareFuncs"].keys())
    supported["export"] = ["not", "currently", "implemented"]
    
    class SetEncoder(json.JSONEncoder):
        def default(self, obj):
            if isinstance(obj, set):
                return list(obj)
            return super().default(obj)
    
    return json.dumps(supported, cls=SetEncoder)
    
@app.route('/api_presearch')
def presearch():
    searchJSON = json.loads(flask.request.data)
    translateObj = {
        "dbName" : {dbData.prettyName : db for db, dbData in prefs["staticDBInfo"].dbs},
        "colName" : null,
        "searchValue" : null,
        "compareFunc" : nassGlobal.prefs["supportedCompareFuncs"]
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