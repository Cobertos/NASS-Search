#A simple script to explore SAS7BDAT files interactively
#Windows only due to msvcrt
#Doesn't handle end of file (IteratorStop exception)
import os.path
import sys
import msvcrt

from sas7bdat import SAS7BDAT

def aStr(a):
    return "[" + ",".join(a) + "]"
    
def main():
    print("Sas7bDat Summary == WINDOWS ONLY")
    if len(sys.argv) < 3:
        print("Usage: sasSummary.py [mode] [.sas7bdat file or filename]")
        sys.exit()
        
    filePath = sys.argv[2]
    if(sys.argv[1] == "i" or sys.argv[1] == "e"):
        with SAS7BDAT(filePath, skip_header=True) as db:
            if(sys.argv[1] == "i"):
                print("f for forward, b for backward, q to quit\n")
                print("COLUMNS")
                #Decode some of the information
                cols = [col.name.decode(db.encoding, db.encoding_errors) for col in db.columns]
                print(aStr(cols))
                print("")
                
                dbPos = 0
                lookPos = 0
                rowCache = dict()
                inChar = None
                dbItr = iter(db)
                while True:
                    #Get current look row
                    if lookPos >= dbPos:
                        row = [str(a) for a in dbItr.__next__()]
                        dbPos+=1
                        rowCache[lookPos] = row
                    else:
                        row = rowCache[lookPos]
                        
                    print("P:" + str(lookPos) + " " + aStr(row))
                    
                    #Get the control character and do stuff
                    inChar = msvcrt.getch().decode("ascii", "strict")
                    
                    if inChar == "q":
                        sys.exit()
                    elif inChar == "b":
                        lookPos-=1
                        if lookPos < 0:
                            lookPos = 0
                    elif inChar == "f":
                        lookPos+=1
            elif(sys.argv[1] == "e"):
                exportFilePath = os.path.splitext(filePath)[0] + "_export.csv"
                print("EXPORTING TO " + exportFilePath)
                f = open(exportFilePath, "w")
            
    if(sys.argv[1] == "ea"): #Must be performed in the base directory
        filePathBase = "./nassDB/"
        filePathSecondBase = "/Unformatted Data/"
        exportFileName = sys.argv[2]
        
        writeFilePath = "./" + exportFileName + ".csv_but_with_tildes"
        f = open(writeFilePath, "w")
        f.write("\n")
        print("EXPORTING TO " + writeFilePath)
        for year in ["2010", "2011", "2012", "2013"]:
            readFilePath = filePathBase + year + filePathSecondBase + exportFileName + ".sas7bdat"
            print("EXPORTING FROM " + readFilePath)
            with SAS7BDAT(readFilePath, skip_header=True) as db:
                for row in db:
                    row = [str(a) for a in row]
                    f.write("~".join(row) + "~" + year + "\n")
            

#Argv[1] == i (interactive), e (export), ea (export all)
if __name__ == "__main__":
    main()