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

    tags = sys.argv[2:]

    
        

    con.create_function("compute", 2, computeDist)

    con.commit()

    # Computing the distance 

    cmd1 = '''
    WITH temp(wid, ordinal, nid) AS(
        SELECT wt.id, wp.ordinal, wp.nodeid
        FROM waytag wt, waypoint wp
        WHERE wt.id = wp.wayid AND 
    '''
    cmd2 = ''
    j = 1
    for i in tags:
        
        k, v = i.split('=')
        temp = '(k = "%s" AND v = "%s")'%(k, v)

        if(len(tags) > j):
            temp = temp + ' OR '
        j += 1
        cmd2 = cmd2 + temp

    cmd3 = '''
    ),
    distance(wid, dist) AS(
        SELECT t1.wid, compute(t1.nid, t2.nid)
        FROM temp t1, temp t2
        WHERE t1.wid = t2.wid AND t1.ordinal = t2.ordinal + 1
    ),
    answer(wid, dist) AS(
        SELECT COUNT(DISTINCT d.wid), MAX(d.dist)
        FROM distance d
    )


    SELECT *
    FROM answer'''

    cmd = cmd1+cmd2+cmd3
    
    cur.execute(cmd)

    try:
        data = cur.fetchone()

        print(data[0], (data[1]))
    except:
        print("error")
    

    
# connect to database

db = sys.argv[1]

con = sqlite3.connect(db)

cur = con.cursor()

cur.execute("PRAGMA foreign_keys = ON;")

if __name__ == "__main__":
    main()