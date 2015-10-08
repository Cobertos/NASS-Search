import threading

from nassAPI.nassSearchTerm import NASSSearchTerm, NASSSearch
from nassAPI.nassCase import NASSCase

class NASSSearchWorker(threading.Thread):
    def __init__(self, search, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.search = search
        self.status = "NEW"
        
    def run(self):
        #Perform the search
        self.status = "SEARCH"
        self.search.perform()
        if self.status == "CANCELLING":
            self.status = "CANCELLED"
            return
            
        #Export the cases
        self.status = "EXPORT"
        self.cases = self.search.export("links")
        if self.status == "CANCELLING":
            self.status = "CANCELLED"
            return
        
        self.status = "DONE"
        
    def getStatus(self):
        return self.status
        
    def cancel(self):
        self.status = "CANCELLING"