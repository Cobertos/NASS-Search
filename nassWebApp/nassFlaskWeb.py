import json
import os
import mimetypes
import random
import sys
import codecs
   
from flask import Flask, url_for, redirect, abort, request
app = Flask("NASS")
app.debug = True

sys.path.append(os.path.realpath(".."))
import nassAPI.nassGlobal as nassGlobal
import nassAPI.nassSearchTerm as nassSearchTerm
from nassWorkers import NASSSearchWorker

#NASS redirect
nassGlobal.updateUserPrefs({
    "rootPath" : os.path.realpath(".."),
})

def jsonToNASSSearch(jsonData):
    jsonObj = json.loads(jsonData)
    translateObj = {
        "dbName" : None, #{dbData.prettyName : db for db, dbData in prefs["staticDBInfo"].dbs},
        "colName" : None,
        "searchValue" : None,
        "compareFunc" : nassGlobal.prefs["supportedCompareFuncs"]
    }
    return nassSearchTerm.NASSSearchTerm.fromJSON(jsonObj, translateObj)
    


@app.route('/app/<path:file>')
def serve(file):
    path = "./webFiles/" + file
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
    supported["joinName"] = [enumObj.name for enumObj in nassSearchTerm.NASSSearchJoin]
    supported["compareFunc"] = list(nassGlobal.prefs["supportedCompareFuncs"].keys())
    supported["export"] = ["not", "currently", "implemented"]
    
    class SetEncoder(json.JSONEncoder):
        def default(self, obj):
            if isinstance(obj, set):
                return list(obj)
            return super().default(obj)
    
    return json.dumps(supported, cls=SetEncoder)
    
@app.route('/api_presearch', methods=["POST"])
def presearch():
    requestData = codecs.decode(request.data, "utf_8");
    searchTerm = jsonToNASSSearch(requestData)
    searchDicts = searchTerm.dictTerms()
    searchLookupDict = {}
    for d in searchDicts:
        for k, v in d.items():
            if not k in searchLookupDict:
                searchLookupDict[k] = set()
            searchLookupDict[k].add(v)
    for k, v in searchLookupDict.items():
        searchLookupDict[k] = list(v)
    
    
    #Do the presearch, generate alerts
    alerts = []
    #Alerts for years excluded
    for year, yearData in nassGlobal.data["preprocessDBInfo"].items():
        shouldBreak = False
        #ALERT TYPE: Database not in year of range
        for db in searchLookupDict["dbName"]:
            if not db in yearData["dbs"].keys():
                alerts.append({
                    "name" : "Year " + year + " excluded",
                    "shortName" : year + " EXCL",
                    "type" : "exclusion",
                    "description" : "The year " + year + " does not contain an entry for database " + db + " (which is in your search terms) and so year " + year + " will be excluded."
                })
                break
                
            #ALERT TYPE: Column not in database of a given year
            for col in searchLookupDict["colName"]:
                if not col in yearData["dbs"][db]["columnNames"]:
                    alerts.append({
                        "name" : "Year " + year + " excluded",
                        "shortName" : year + " EXCL",
                        "type" : "exclusion",
                        "description" : "The year " + year + " contains database " + db + " but does not have column " + col + " and so will be excluded."
                    })
                    shouldBreak = True
                    break
            if shouldBreak:
                shouldBreak = False
                break
                
    
    return json.dumps(alerts)

workers = []
    
@app.route('/api_search', methods=["POST"])
def search():
    #Spawn a new thread to search
    requestData = codecs.decode(request.data, "utf_8");
    searchTerm = jsonToNASSSearch(requestData)
    worker = NASSSearchWorker(searchTerm)
    
    #Put it in the array based on jobId
    jobId = random.randint(0,sys.maxsize)
    workers[jobId] = worker
    return jobId
    
@app.route('/api_searchPoll', methods=["POST"])
def searchPoll():
    requestData = codecs.decode(request.data, "utf_8");
    jsonObj = json.loads(requestData)
    
    if not (jsonObj["jobId"] in workers):
        return "JobId does not exist"
    
    worker = workers[jsonObj["jobId"]]
    action = jsonObj["action"]
    if action == "CANCEL":
        worker.cancel()
    
    return worker.getStatus()

if __name__ == "__main__":
    app.run()