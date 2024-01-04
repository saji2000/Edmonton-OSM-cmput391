# Q1 -- Load OSM Data into SQLite

Checklist:
* read up on the [OSM data model](http://wiki.openstreetmap.org/wiki/Elements) 
* install [Osmosis](http://wiki.openstreetmap.org/wiki/Osmosis)
* download a recent map of Alberta from the [Canadian section of the Geofabrik.de download site](https://download.geofabrik.de/north-america/canada.html)
* get the MBR of Edmonton from [the official boundaries of the City of Edmonton](https://data.edmonton.ca/Administrative/City-of-Edmonton-Corporate-Boundary/m45c-6may)
* use osmosis to extract all nodes and paths (with their tags) of Edmonton into an XML file
* process that file to extract the tuples into the SQLite database
* make sure the database has all constraints defined
* make sure your `.gitignore` file prevents you from uploading binary files or large XML files to GitHub (and make sure no such files exist in your repository as well)


To create the database run the following command in the q1 directory

./terminalCommand

It will download and create the database for q1



## SQL DDL 

Write the DDL for your database here, including all constraints. 

```SQL
CREATE TABLE IF NOT EXISTS node (id integer, lat float, lon float, PRIMARY KEY (id))

CREATE TABLE IF NOT EXISTS nodetag (id integer , k text, v text, FOREIGN KEY (id) REFERENCES node(id) ON DELETE CASCADE)

CREATE TABLE IF NOT EXISTS way (id integer, closed boolean, PRIMARY KEY (id))

CREATE TABLE IF NOT EXISTS waypoint (wayid integer, ordinal integer, nodeid integer, FOREIGN KEY (wayid) REFERENCES way(id) ON DELETE CASCADE, FOREIGN KEY (nodeid) REFERENCES node(id) ON DELETE CASCADE)

CREATE TABLE IF NOT EXISTS waytag (id integer, k text, v text, FOREIGN KEY (id) REFERENCES way(id) ON DELETE CASCADE)

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
```
