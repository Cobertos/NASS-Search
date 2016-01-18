"""
Worker thread for the web application

A worker that performs a search and responds with its status to provide to an
overseeing user
"""

import random
import threading
import time
import sys

from nassAPI.nassSearchTerm import NASSSearchTerm, NASSSearch
from nassAPI.nassCase import NASSCase

class NASSSearchWorkerManager():
    """
    Manages all current NASSSearchWorkers
    """
    def __init__(self):
        self.workers = {}
        
    def getNewWorker(self, search, start=False):
        jobId = str(random.randint(0,sys.maxsize)) #Randomize jobId
        self.workers[jobId] = newWorker = NASSSearchWorker(search)
        
        if start:
            newWorker.start()
        return jobId
        
    def getWorker(self, jobId):
        return self.workers[jobId]
    

class NASSSearchWorker(threading.Thread):
    """
    Seperate thread to run a search in with ability to get status updates
    """
    
    def __init__(self, search, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.search = NASSSearch(search)
        self.status = "NEW"
        self.caseCount = 0
        self.cases = None
        
    def run(self):
        try:
            for status in self.perform():
                if self.status == "CANCELLING":
                    self.status = "CANCELLED"
                    return
                    
                self.status = status    
                self.caseCount = len(self.search.foundCases)
                
                if self.status == "DONE":
                    return
                    
        except Exception as e:
            import traceback
            traceback.print_exc()
            self.status = "FAILED [" + e.__class__.__name__ + "]"
            return
    
    def perform(self):
        #Perform the search
        for complete in self.search.performResponsive():
            if not complete:
                yield "SEARCHING"
            else:
                break
            
        #Export the cases
        yield "DONE"
        self.cases = self.search.export("links")
        
        yield "RETURNING"
        
    def getStatus(self):
        return self.status
    
    def getCaseCount(self):
        return self.caseCount
        
    def getCases(self):
        return self.cases
    
    def cancel(self):
        self.status = "CANCELLING"