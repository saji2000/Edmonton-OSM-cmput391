import xml.sax
import sqlite3
import os

class NodeHandler( xml.sax.ContentHandler ):
   def __init__(self, cur, con):
      self.CurrentData = ""
      self.nodeId = ""
      self.lat = ""
      self.lon = ""
      self.k = ""
      self.v = ""
      self.cur = cur
      self.con = con
      self.wayid = ""
      self.ref = ""
      self.wayfirstref = ""
      self.isfirstwaypoint = False
      self.iswayclosed = False

      self.waypointcount = 1
       
   # Call when an element starts
   def startElement(self, tag, attributes):
      self.CurrentData = tag
      
      if tag == "node":
         self.nodeId = attributes["id"]
         self.lat = attributes["lat"]
         self.lon = attributes["lon"]

         self.cur.execute("INSERT INTO node (id, lat, lon) VALUES(?, ?, ?)",(self.nodeId, self.lat, self.lon))

      elif tag == "tag" and self.nodeId != "":
         self.k = attributes["k"]
         self.v = attributes["v"]

      elif tag == "way":
         self.wayid = attributes["id"]
         self.isfirstwaypoint = True

         self.cur.execute("INSERT INTO way (id, closed) VALUES(?, ?)",(self.wayid, self.iswayclosed))
      elif tag == "nd":
         self.ref = attributes["ref"]  
      
      elif tag == "tag" and self.wayid != "":
         self.k = attributes["k"]
         self.v = attributes["v"]
   # Call when an elements ends
   def endElement(self, tag):
      if tag == "node":
         # Node
         self.nodeId = ""
         self.lat = ""
         self.lon = ""

      elif tag == "tag" and self.nodeId != "":
         # Node tag
         self.cur.execute("INSERT INTO nodetag (id, k, v) VALUES(?, ?, ?)",(self.nodeId, self.k, self.v))

         self.k = ""
         self.v = ""
      elif tag == "way":
         
         self.cur.execute("UPDATE way SET closed=? WHERE id=?",(self.iswayclosed, self.wayid))

         self.wayid = ""
         self.iswayclosed = False
         self.waypointcount = 1
      elif tag == "nd":
         self.iswayclosed = False   # set to False if previous waypoint set to true, since it's not the last element

         # skip the current node if it doesn't exist in edmonton, it should already be inserted into the database
         self.cur.execute("SELECT * FROM node WHERE id=?", (self.ref,))
         rows = cur.fetchall()
         if not rows: return

         if self.isfirstwaypoint:
            # This is the first way point
            self.wayfirstref = self.ref
         elif self.wayfirstref == self.ref:
            # the waypoint matches the 
            self.iswayclosed = True

         self.cur.execute("INSERT INTO waypoint (wayid, ordinal, nodeid) VALUES(?, ?, ?)",(self.wayid, self.waypointcount, self.ref))

         self.isfirstwaypoint = False
         self.waypointcount += 1
      elif tag == "tag" and self.wayid != "":
         self.cur.execute("INSERT INTO waytag (id, k, v) VALUES(?, ?, ?)",(self.wayid, self.k, self.v))

         self.k = ""
         self.v = ""

   # Call when a character is read
   def characters(self, content):
       pass

filePath = 'edmonton.db'
if os.path.exists(filePath):
    print("Deleted old edmonton.db")
    os.remove(filePath)


con = sqlite3.connect('edmonton.db')
cur = con.cursor()
cur.execute('PRAGMA foreign_keys = ON')


cur.execute('CREATE TABLE IF NOT EXISTS node (id integer, lat float, lon float, PRIMARY KEY (id))')
cur.execute('CREATE TABLE IF NOT EXISTS nodetag (id integer , k text, v text, FOREIGN KEY (id) REFERENCES node(id) ON DELETE CASCADE)')
cur.execute('CREATE TABLE IF NOT EXISTS way (id integer, closed boolean, PRIMARY KEY (id))')
cur.execute('CREATE TABLE IF NOT EXISTS waypoint (wayid integer, ordinal integer, nodeid integer, FOREIGN KEY (wayid) REFERENCES way(id) ON DELETE CASCADE, FOREIGN KEY (nodeid) REFERENCES node(id) ON DELETE CASCADE)')
cur.execute('CREATE TABLE IF NOT EXISTS waytag (id integer, k text, v text, FOREIGN KEY (id) REFERENCES way(id) ON DELETE CASCADE)')
con.commit()



# create an XMLReader
parser = xml.sax.make_parser()
# turn off namepsaces
parser.setFeature(xml.sax.handler.feature_namespaces, 0)

# override the default ContextHandler
Handler = NodeHandler(cur, con)
parser.setContentHandler(Handler)

parser.parse("edmonton.osm")

print("finished")
con.commit()


# Trevor Trigger
trigInsert1 = '''
CREATE TRIGGER trigInsert1
AFTER INSERT ON waypoint
WHEN (
        SELECT *
        FROM (
            SELECT nodeid FROM waypoint WHERE wayid = new.wayid ORDER BY ordinal LIMIT 1
        )
        INTERSECT
        SELECT *
        FROM (
            SELECT nodeid FROM waypoint WHERE wayid = new.wayid ORDER BY ordinal DESC LIMIT 1
        )
    ) IS NOT NULL
BEGIN
UPDATE way SET closed = True WHERE id = new.wayid;
END;
'''

trigInsert2 = '''
CREATE TRIGGER trigInsert2
AFTER INSERT ON waypoint
WHEN (
        SELECT *
        FROM (
            SELECT nodeid FROM waypoint WHERE wayid = new.wayid ORDER BY ordinal LIMIT 1
        )
        INTERSECT
        SELECT *
        FROM (
            SELECT nodeid FROM waypoint WHERE wayid = new.wayid ORDER BY ordinal DESC LIMIT 1
        )
    ) IS NULL
BEGIN
UPDATE way SET closed = False WHERE id = new.wayid;
END;
'''

trigUpdate1 = '''
CREATE TRIGGER trigUpdate1
AFTER Update ON waypoint
WHEN (
        SELECT *
        FROM (
            SELECT nodeid FROM waypoint WHERE wayid = new.wayid ORDER BY ordinal LIMIT 1
        )
        INTERSECT
        SELECT *
        FROM (
            SELECT nodeid FROM waypoint WHERE wayid = new.wayid ORDER BY ordinal DESC LIMIT 1
        )
    ) IS NULL
BEGIN
UPDATE way SET closed = False WHERE id = new.wayid;
END;
'''

trigUpdate2 = '''
CREATE TRIGGER trigUpdate2
AFTER UPDATE ON waypoint
WHEN (
        SELECT *
        FROM (
            SELECT nodeid FROM waypoint WHERE wayid = new.wayid ORDER BY ordinal LIMIT 1
        )
        INTERSECT
        SELECT *
        FROM (
            SELECT nodeid FROM waypoint WHERE wayid = new.wayid ORDER BY ordinal DESC LIMIT 1
        )
    ) IS NULL
BEGIN
UPDATE way SET closed = False WHERE id = new.wayid;
END;
'''

trigDelete1 = '''
CREATE TRIGGER trigDelete1
AFTER DELETE ON waypoint
WHEN (
        SELECT *
        FROM (
            SELECT nodeid FROM waypoint WHERE wayid = old.wayid ORDER BY ordinal LIMIT 1
        )
        INTERSECT
        SELECT *
        FROM (
            SELECT nodeid FROM waypoint WHERE wayid = old.wayid ORDER BY ordinal DESC LIMIT 1
        )
    ) IS NULL
BEGIN
UPDATE way SET closed = False WHERE id = old.wayid;
END;
'''

trigDelete2 = '''
CREATE TRIGGER trigDelete2
AFTER DELETE ON waypoint
WHEN (
        SELECT *
        FROM (
            SELECT nodeid FROM waypoint WHERE wayid = old.wayid ORDER BY ordinal LIMIT 1
        )
        INTERSECT
        SELECT *
        FROM (
            SELECT nodeid FROM waypoint WHERE wayid = old.wayid ORDER BY ordinal DESC LIMIT 1
        )
    ) IS NULL
BEGIN
UPDATE way SET closed = False WHERE id = old.wayid;
END;
'''



cur.execute(trigInsert1)
cur.execute(trigInsert2)
cur.execute(trigUpdate1)
cur.execute(trigUpdate2)
cur.execute(trigDelete1)
cur.execute(trigDelete2)

# Sajjad's triggers

ordTrigInsert = '''
CREATE TRIGGER ordTrigInsert
BEFORE INSERT ON waypoint 
WHEN  EXISTS(
	SELECT *
	FROM waypoint
	WHERE new.ordinal <= ordinal AND new.wayid = wayid)
BEGIN
    UPDATE waypoint 
    SET ordinal = ordinal + 1
    WHERE new.ordinal <= ordinal AND new.wayid = wayid;
END;
'''

ordTrigUpdate = '''
CREATE TRIGGER ordTrigUpdate
BEFORE UPDATE ON waypoint 
WHEN  EXISTS(
	SELECT *
	FROM waypoint
	WHERE new.ordinal <= ordinal AND new.wayid = wayid)
BEGIN
    UPDATE waypoint 
    SET ordinal = ordinal + 1
    WHERE new.ordinal <= ordinal AND new.wayid = wayid;
END;
'''

ordTrigDelete = '''
CREATE TRIGGER ordTrigDelete
BEFORE DELETE ON waypoint 
WHEN  EXISTS(
	SELECT *
	FROM waypoint
	WHERE old.ordinal <= ordinal AND old.wayid = wayid)
BEGIN
    UPDATE waypoint 
    SET ordinal = ordinal - 1
    WHERE old.ordinal <= ordinal AND old.wayid = wayid;
END;
'''
cur.execute(ordTrigInsert)
cur.execute(ordTrigUpdate)
cur.execute(ordTrigDelete)

con.commit()

con.close()


