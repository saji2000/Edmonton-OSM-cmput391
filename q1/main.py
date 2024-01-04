# Python program to read
# json file
 
import os
import json

# Opening JSON file
f = open('myfile.json',)
 
# returns JSON object as
# a dictionary
data = json.load(f)

# getting the a string of coordinates
dataString = data['data'][0][8][16:-3]

# Create a list of tuple for lat and long
coordinates = []
for i in dataString.split(", "):
    tempTuple = tuple(i.split(" ")[:])
    tempTuple = (float(tempTuple[0]), float(tempTuple[1]))
    coordinates.append(tempTuple)

maxLon = coordinates[0][0]
minLon = coordinates[0][0]
maxLat = coordinates[0][1]
minLat = coordinates[0][1]

for i in coordinates:
    maxLon = max(maxLon, i[0])
    minLon = min(minLon, i[0])
    maxLat = max(maxLat, i[1])
    minLat = min(minLat, i[1])

print(maxLon)
print(minLon)
print(maxLat)
print(minLat)

# using os.system to run the commands and get the edmonton.osm

cmd1 = 'osmosis --read-pbf "alberta-latest.osm.pbf"'
cmd2 = ' --bounding-box bottom={0} left={1} top={2} right={3}'.format(minLat, minLon, maxLat, maxLon)
cmd3 = ' --write-xml edmonton.osm'
cmd = cmd1+cmd2+cmd3
os.system(cmd)

# Closing file
f.close()