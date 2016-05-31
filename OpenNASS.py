

#All the functionality for OpenNASS, the actual system using the API and Flask web stuff
def setup():
    #Download the stuff from NASS website

    #Preprocess all the information
    from nassAPI import nassPreprocess
    nassPreprocess.main()


def run():
    #Open OpenNASS and runs it
    import os
    os.chdir("./nassWebApp")
    
    import subprocess
    subprocess.Popen(["python", "nassFlaskWeb.py"])
    
    import webbrowser
    webbrowser.open("http://127.0.0.1:5000")
    
def main():
    run()
    
    
if __name__ == "__main__":
    print("This file is not fully implemented yet")