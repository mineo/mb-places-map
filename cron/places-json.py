#!/usr/bin/python
"""
Usage: places-json.py path-to-target-json-file
"""
import geojson
import requests
import sys

from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.orm import aliased, relationship, sessionmaker
from sqlalchemy import and_, create_engine, func
from mbdata.models import Event, Place, LinkEventPlace, LinkPlaceURL, URL

Place.event_links = relationship("LinkEventPlace")
Place.events = association_proxy("event_links", "event")

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


def convert_to_geojson(places_dict):
    feature_collection = geojson.FeatureCollection([])
    for gid, place in places_dict.iteritems():
        c = place["coordinates"]
        point = geojson.Point((c[1], c[0]))
        feature = geojson.Feature(id=gid, geometry=point)
        place.pop("coordinates")
        feature["properties"] = place
        feature_collection["features"].append(feature)
    return feature_collection


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
        places[place.gid] = {'name': place.name,
                             'coordinates': place.coordinates,
                             'commons_link': url,
                             'events': []
                             }

    ev_alias = aliased(Event)

    stmt = s.query(Place.id.label("place_id"),
                   ev_alias.id.label("event_id"),
                   func.row_number().over(partition_by=Place.id,
                                          order_by=ev_alias.begin_date).
                   label("row_num"))\
        .outerjoin(LinkEventPlace)\
        .outerjoin(ev_alias)\
        .order_by(ev_alias.begin_date)\
        .cte()

    event_query = s.query(Place.gid.label("place_gid"),
                          ev_alias)\
        .join(stmt, Place.id == stmt.c.place_id)\
        .join(LinkEventPlace, Place.id == LinkEventPlace.entity1_id)\
        .join(ev_alias, ev_alias.id == LinkEventPlace.entity0_id)\
        .filter("row_num < 3")\
        .filter(Place.coordinates != None)

    for place_gid, event in event_query:
        places[place_gid]['events'].append(
            {'gid': event.gid,
             'name': event.name,
             }
        )

    json_filename = sys.argv[1]

    update_thumbnail_links(places)

    feature_collection = convert_to_geojson(places)

    with open(json_filename, "w") as fp:
        geojson.dump(feature_collection, fp)
