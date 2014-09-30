#!/usr/bin/python
"""
Usage: places-json.py path-to-target-json-file
"""
import json
import psycopg2 as pg
import psycopg2.extras as pgex
import re
import requests
import sys

from os.path import isfile
from urlparse import urlparse, urlunparse
from time import sleep


THUMB_SIZE = 250
QUERY = {"action": "query",
         "prop": "imageinfo",
         "iiprop": "url",
         "iiurlwidth": THUMB_SIZE,
         "format": "json"}
MAX_FILES_PER_REQUEST = 50
HEADERS = {"User-Agent": "mb-places-map (https://de.wikipedia.org/wiki/Benutzer:Mineo; Mineo@Freenode)"}


def do_request(places, filenames):
    titles = "|".join(filenames.keys())
    newquery = QUERY.copy()
    newquery["titles"] = titles
    url = urlunparse(("https",
                      "commons.wikimedia.org",
                      "/w/api.php",
                      "",
                      "",
                      ""))
    r = requests.get(url, params=newquery, headers=HEADERS)
    if not r.ok:
        print r.status_code, " on ", r.url
        return
    resp = r.json()

    # Maps normalized filenames back to their original ones
    normalizations = {}
    for norm in resp["query"]["normalized"]:
        normalizations[norm["to"]] = norm["from"]

    # Insert the thumbnail links back into `places`
    for v in resp["query"]["pages"].itervalues():
        if "imageinfo" in v:
            filename = normalizations.get(v["title"], v["title"])
            mbid = filenames[filename]
            places[mbid]["thumbnail_link"] = v["imageinfo"][0]["thumburl"]


def update_thumbnail_links(places):
    # Maps filenames to MBIDs
    filenames = {}
    for mbid, v in places.copy().iteritems():
        if v["commons_link"] is not None and "thumbnail_link" not in v:
            filenames[urlparse(v["commons_link"]).path.strip("/wiki/")] = mbid

        if len(filenames) == MAX_FILES_PER_REQUEST:
            do_request(places, filenames)
            filenames = {}
            sleep(1)

if __name__ == "__main__":
    if not len(sys.argv) == 2:
        exit(__doc__)

    db = pg.connect("dbname=musicbrainz_db_slave user=musicbrainz host=127.0.0.1")
    cur = db.cursor(cursor_factory=pgex.NamedTupleCursor)
    cur.execute("""
    WITH places_urls AS (
        SELECT p.gid as gid, u.url as url
        FROM place p
        JOIN l_place_url lpu ON lpu.entity0 = p.id
        JOIN link l on lpu.link = l.id
        JOIN link_type lt on l.link_type = lt.id
        JOIN url u on lpu.entity1 = u.id
        WHERE p.coordinates IS NOT NULL
        AND lt.gid = '68a4537c-f2a6-49b8-81c5-82a62b0976b7'
        AND url LIKE '%commons.wikimedia.org%'
    )
    SELECT DISTINCT ON (p.gid) p.gid as gid, p.name as name, p.coordinates as coordinates, pu.url as url
    FROM place p
    LEFT JOIN places_urls pu on p.gid = pu.gid
    WHERE p.coordinates IS NOT NULL;
    """)

    places = {}
    for result in cur:
        coords = result.coordinates
        m = re.match(r"\(([^)]+),([^)]+)\)", coords)
        places[result.gid] = {'name': result.name,
                              'coordinates': [float(m.group(1)), float(m.group(2))],
                              'commons_link': result.url
                              }

    json_filename = sys.argv[1]
    if isfile(json_filename):
        with open(json_filename, "r") as fp:
            oldplaces = json.load(fp)
        for k, v in places.iteritems():
            if k in oldplaces and "thumbnail_link" in oldplaces[k]:
                places[k]["thumbnail_link"] = oldplaces[k]["thumbnail_link"]

    update_thumbnail_links(places)

    with open(json_filename, "w") as fp:
        json.dump(places, fp)
