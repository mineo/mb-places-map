#!/usr/bin/python
import json
import re
import pprint
import psycopg2 as pg
db = pg.connect("dbname=musicbrainz_db_slave user=musicbrainz host=127.0.0.1")
cur = db.cursor()
cur.execute("SELECT name, coordinates FROM place WHERE coordinates IS NOT NULL;")
places = {}
for result in cur:
	coords = result[1]
	m = re.match(r"\(([^)]+),([^)]+)\)", coords)
	places[result[0]] = [float(m.group(1)), float(m.group(2))]
with open("/home/mineo/public_html/places/places.json", "w") as fp:
	#pprint.pprint(json.dumps(places))
	json.dump(places, fp)
