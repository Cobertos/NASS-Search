#A simple script to give a summary of a .sas7bdat file
#Mainly for exploring the files that SAS includes to see if it's worth looking into
import sys

from sas7bdat import SAS7BDAT

if __name__ == "__main__":
    print("Sas7bDat Summary\n")
    if len(sys.argv) != 2:
        print("Usage: sasSummary.py [.sas7bdat file]")
        sys.exit()
        
    filePath = sys.argv[1]
    with SAS7BDAT(filePath) as db:
        print("COLUMNS")
        #Decode some of the information
        for col in db.columns:
            print(col.name.decode(db.encoding, db.encoding_errors))

        input("Press ENTER to continue...")
        
        print("\nEXAMPLE DATA")
        count = 0
        for row in db:
            print("\nEXAMPLE SET #" + str(count+1))
            for v in row:
                print(v)
            input("Press ENTER to continue...")
            
            count+=1
            if count>5:
                sys.exit()
        