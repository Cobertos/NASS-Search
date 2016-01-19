import json
import os
import mimetypes
import sys
import codecs
   
from flask import Flask, url_for, redirect, abort, request
app = Flask("NASS")
app.debug = True

sys.path.append(os.path.realpath(".."))
import nassAPI.nassGlobal as nassGlobal
import nassAPI.nassSearchTerm as nassSearchTerm
from nassWorkers import NASSSearchWorker, NASSSearchWorkerManager

workerManager = NASSSearchWorkerManager()

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
    
#MAIN SERVING ROUTE
@app.route('/app/<path:file>')
def serve(file):
    """
    Serves a file to the web user
    
    Be warned this should not be used on a public server
    """
    
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

#AJAX REQUESTS
@app.route('/api_init')
def init():
    """
    Ajax response for init request. Responds with all supported operations and data
    """

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
    """
    Ajax response for a presearch request
    
    A presearch takes a search and returns and alerts that may occur given the
    data it is searching. An example alert would be that a given year is excluded
    and the reason that we need to exclude that year from the search
    """

    requestData = codecs.decode(request.data, "utf_8");
    searchTerm = jsonToNASSSearch(requestData)
    searchDicts = searchTerm.allTermDicts()
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
 
@app.route('/api_search', methods=["POST"])
def search():
    """
    Ajax response to a search request
    
    Responds to a request to search with the job id of the newly created search
    """
    
    global workerManager
    
    #Spawn a new thread to search
    requestData = codecs.decode(request.data, "utf_8")
    searchTerm = jsonToNASSSearch(requestData)
    jobId = workerManager.getNewWorker(searchTerm, start=True)
    
    jsonOut = {}
    jsonOut["jobid"] = jobId
    return json.dumps(jsonOut)
    
@app.route('/api_searchPoll', methods=["POST"])
def searchPoll():
    """
    Ajax response to search poll
    
    Responds to a request to poll for data on a given search
    """
    
    global workerManager

    requestData = codecs.decode(request.data, "utf_8")
    jsonObj = json.loads(requestData)
    
    try:
        worker = workerManager.getWorker(jsonObj["jobid"])
    except:
        abort(500)
    
    #Check what the client wants to perform
    if "action" in jsonObj:
        action = jsonObj["action"]
        if action == "CANCEL":
            worker.cancel()
            
    #Check what we should return
    if worker.getStatus() == "DONE":
        ret = (worker.getStatus(), worker.getCases())
    else:
        ret = (worker.getStatus(), worker.getCaseCount())
    return json.dumps(ret, cls=nassGlobal.NASSJSONEncoder)

if __name__ == "__main__":
    app.run()