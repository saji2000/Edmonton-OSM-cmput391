import sqlite3
from math import radians, sin, cos, asin, sqrt
import sys


def computeDist(node1, node2):

    con = sqlite3.connect(db)

    cur = con.cursor()
    # Getting the lat and lon for the first node
    cur.execute("SELECT lat, lon FROM node WHERE id = ?", (node1,))

    try:
        lat1, lon1 = cur.fetchone()
    except:
        return "error"

    # Getting the lat and lon for the second node
    cur.execute("SELECT lat, lon FROM node WHERE id = ?", (node2,))

    try:
        lat2, lon2 = cur.fetchone()
    except:
        return "error"

    
    # convert decimal degrees to radians 
    lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])

    # haversine formula 
    dlon = lon2 - lon1 
    dlat = lat2 - lat1 
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * asin(sqrt(a)) 
    r = 6371 # Radius of earth in kilometers
    return round(c * r * 1000)


def main():    

    con.create_function("compute", 2, computeDist)

    con.commit()


    # getting the first and second node id

    node1 = sys.argv[2]


    node2 = sys.argv[3]

    
    cur.execute("SELECT compute(?, ?)", (node1, node2))

    print(cur.fetchone()[0])

    con.commit()

    con.close()

# connect to database

db = sys.argv[1]

con = sqlite3.connect(db)

cur = con.cursor()

cur.execute("PRAGMA foreign_keys = ON;")
    

if __name__ == "__main__":
    main()