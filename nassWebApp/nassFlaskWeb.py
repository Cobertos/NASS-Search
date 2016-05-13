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

def getInitData():
    """
    Returns a dict of all the supported values
    
    Contains:
    year: The years we can search over
    dbName: The name of the databases we can search over
    colName: A dict of dbNames to colNames we can search for
    searchValue: [TODO] A dict of colNames to possible values, if no key for colName assume anything supported
    joinName: The joins that can be used to concatenate logical things
    compareFunc: The comparison functions that can be used to compare searchValues
    export: The supported export formats
    """

    #TODO: Supported shouldn't change while the server is running, can cache this for all requests
    
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
    return supported

def getAlertsFromSearchTerm(searchTerm):
    """
    Generates alerts for a search term
    
    Alerts are possible ommisions or conflicts that arise with a given set of search
    terms. An example alert would be that a given year is excluded and the reason that
    we need to exclude that year from the search such as that a given year does not
    contain a column that the user is searching for
    """
    
    #Get each of unique dicts inside of the search term
    searchDicts = searchTerm.allTermDicts()
    #Get the used values in all dict keys for all dict terms as sets then lists
    #Currently unneeded
    """searchLookupDict = {
        "dbName" : set(),
        "colName" : set(),
        "searchValue" : set(),
        "compareFunc" : set()
    }
    for d in searchDicts:
        for k, v in d.items():
            if not k in searchLookupDict:
                searchLookupDict[k] = set()
            searchLookupDict[k].add(v)
    for k, v in searchLookupDict.items():
        searchLookupDict[k] = list(v)"""
    
    
    #Do the presearch, generate alerts
    alerts = []
    #Alerts for years excluded
    for year, yearData in nassGlobal.data["preprocessDBInfo"].items():
        for searchDict in searchDicts:
            #ALERT TYPE: Database not in year of range
            if not searchDict["dbName"] in yearData["dbs"].keys():
                alerts.append({
                    "name" : "Year " + year + " excluded",
                    "shortName" : year + " EXCL",
                    "type" : "exclusion",
                    "description" : "The year " + year + " does not contain an entry for database " + db + " (which is in your search terms) and so year " + year + " will be excluded."
                })
                break
            
            #ALERT TYPE: Column not in database of a given year
            if not searchDict["colName"] in yearData["dbs"][searchDict["dbName"]]["columnNames"]:
                alerts.append({
                    "name" : "Year " + year + " excluded",
                    "shortName" : year + " EXCL",
                    "type" : "exclusion",
                    "description" : "The year " + year + " contains database " + db + " but does not have column " + col + " and so will be excluded."
                })
                break
                
    return alerts



#===
#FLASK ROUTES
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
    
    supported = getInitData()
    
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
    
    A presearch takes a search and returns any information to give the user some
    sort of prediction into search results or problems. Currently returns all the
    alerts (conflicts and ommisions) that their search will causes. See getAlertsFromSearchTerm
    for more information
    """

    requestData = codecs.decode(request.data, "utf_8");
    searchTerm = jsonToNASSSearch(requestData)
    alerts = getAlertsFromSearchTerm(searchTerm)
    
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