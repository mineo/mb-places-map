#!/usr/bin/python
"""
Usage: places-json.py path-to-target-json-file
"""
import json
import psycopg2 as pg
import psycopg2.extras as pgex
import re
import sys

if not len(sys.argv) == 2:
    exit(__doc__)

db = pg.connect("dbname=musicbrainz_db_slave user=musicbrainz host=127.0.0.1")
cur = db.cursor(cursor_factory=pgex.NamedTupleCursor)
cur.execute("SELECT gid, name, coordinates FROM place WHERE coordinates IS NOT NULL;")
places = {}
for result in cur:
    coords = result.coordinates
    m = re.match(r"\(([^)]+),([^)]+)\)", coords)
    places[result.gid] = {'name': result.name,
                          'coordinates': [float(m.group(1)), float(m.group(2))]
                          }
with open(sys.argv[1], "w") as fp:
    json.dump(places, fp)
