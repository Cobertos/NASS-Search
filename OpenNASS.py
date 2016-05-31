

#All the functionality for OpenNASS, the actual system using the API and Flask web stuff
def preprocess():
    """
    Preprocesses all the databases stored in the NASS DB folder
    """
    from nassAPI import nassPreprocess
    nassPreprocess.main()

def setup():
    print("This action is not fully implemented yet")
    return
    """
    Sets up this copy of OpenNASS
    
    Downloads all the files from the FTP and preprocesses them
    """
    #Download the stuff from NASS website
    #Preprocess the databases
    preprocess()

def run():
    print("This action is not fully implemented yet")
    return
    """
    Opens the NASS GUI
    
    Runs the NASS Flask web server and opens the users browser to the page
    """
    
    #Open OpenNASS and runs it
    import os
    os.chdir("./nassWebApp")
    
    import subprocess
    subprocess.Popen(["python", "nassFlaskWeb.py"])
    
    import webbrowser
    webbrowser.open("http://127.0.0.1:5000")

def printUsage():
    print("Usage: python OpenNASS.py [action=run,setup]")
    
def main():
    #Check arguments length
    if len(sys.argv) != 2:
        print("Not enough arguments")
        printUsage()
        return
    
    #Check action
    action = sys.argv[1]
    if action in ["main", "printUsage"] or not action in globals() or not hasattr(globals()[action], '__call__'):
        print("Action does not exist")
        printUsage()
        return
        
    #Call the action
    globals()[action].__call__()
    
    
if __name__ == "__main__":
    main()