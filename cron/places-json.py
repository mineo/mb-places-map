#!/usr/bin/python
"""
Usage: places-json.py path-to-target-json-file
"""
import json
import requests
import sys

from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from sqlalchemy.sql.expression import and_
from mbdata.models import Place, LinkPlaceURL, URL

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
    if "normalized" in resp["query"]:
        for norm in resp["query"]["normalized"]:
            normalizations[norm["to"]] = norm["from"]

    # Insert the thumbnail links back into `places`
    if "pages" in resp["query"]:
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

    e = create_engine("postgresql://musicbrainz@127.0.0.1/musicbrainz_db_slave")
    sess = sessionmaker(bind=e)
    s = sess()

    url_query = s.query(Place.id.label("place_id"),
                        URL.url.label("url"))\
                 .join(LinkPlaceURL)\
                 .join(URL, and_(
                     URL.id == LinkPlaceURL.url_id,
                     URL.url.like("%commons.wikimedia.org%")))\
                 .filter(Place.coordinates !=  None)\
                 .cte()

    place_query = s.query(Place,
                          url_query.c.url)\
        .outerjoin(url_query, Place.id == url_query.c.place_id)\
        .filter(Place.coordinates != None)\

    places = {}
    for place, url in place_query:
        coords = place.coordinates
        places[place.gid] = {'name': place.name,
                             'coordinates': coords,
                             'commons_link': url
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
