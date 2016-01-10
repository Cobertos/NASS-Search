#A simple script to explore SAS7BDAT files interactively
#Windows only due to msvcrt
#Doesn't handle end of file (IteratorStop exception)
import sys
import msvcrt

from sas7bdat import SAS7BDAT

def aStr(a):
    return "[" + ",".join(a) + "]"

if __name__ == "__main__":
    print("Sas7bDat Summary == WINDOWS ONLY")
    print("f for forward, b for backward, q to quit\n")
    if len(sys.argv) != 2:
        print("Usage: sasSummary.py [.sas7bdat file]")
        sys.exit()
        
    filePath = sys.argv[1]
    with SAS7BDAT(filePath, skip_header=True) as db:
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