import sqlite3
import csv
import sys

# Should we also insert into way? How to fix the triggers

# This function processes the first row of the data
def processFirstRow(i, cur):
    # print("First row")
    beenCheck = False
    for j in i:
        # print("The item to be processed: " + j)
        # Checking if it already exists
        if(not beenCheck):
            # print("Has not been checked")
            cur.execute("SELECT * FROM way WHERE id = ?", (j, ))
            id = j

            exists = cur.fetchone()

            # print(exists)
            if(exists is not None):
                # print("exist")
                pass
            else:
                exists = False
                cur.execute("INSERT INTO way VALUES(?, ?)", (id, 0))

            beenCheck = True
        else:
            # print("Tag: " + j)
            # Insert into the waytag table
            k, v = j.split("=")

            cur.execute("INSERT INTO waytag VALUES(?, ?, ?)",(id, k, v))
        
    return exists, id

# This function processes the second row of the data
def processSecondRow(i, cur, id):
    # print("Second row")
    ordinal = 1
    for j in i:
        # print(j)
        cur.execute("INSERT INTO waypoint VALUES(?, ?, ?)", (id, ordinal, j))
        ordinal = ordinal + 1



def main():

                    
    db = sys.argv[1]

    con = sqlite3.connect(db)

    cur = con.cursor()

    cur.execute("PRAGMA foreign_keys = ON;")

    tsv_path = sys.argv[2]

    tsv_file = open(tsv_path)

    tsv_read = csv.reader(tsv_file, delimiter='\t')
    # flag for the next way
    first = True

    for i in tsv_read:

        # print("The row about to be processed: " + str(i))

        if(len(i) == 0):
            first = True
            pass

        else:
            # The first row of data
            if(first):
                exists, id = processFirstRow(i, cur)
                first = False
                
            # The second row of data
            elif(not exists):
                processSecondRow(i, cur, id)

        
    print("success")

    con.commit()

                


if __name__ == "__main__":
    main()