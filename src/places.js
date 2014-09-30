var map = L.map('map-canvas').setView([50.683889,10.919444], 4);
var osmLayer = L.tileLayer('http://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: 'Map data &copy; <a href="http://openstreetmap.org">OpenStreetMap</a> contributors.',
    maxZoom: 19
});
map.addLayer(osmLayer);

var openAerialLayer = L.tileLayer('http://otile{s}.mqcdn.com/tiles/1.0.0/sat/{z}/{x}/{y}.png', {
    attribution: '<p>Tiles Courtesy of <a href="http://www.mapquest.com/" target="_blank">MapQuest</a> <img src="http://developer.mapquest.com/content/osm/mq_logo.png"></p> Portions Courtesy NASA/JPL-Caltech and U.S. Depart. of Agriculture, Farm Service Agency',
    maxZoom: 11,
    subdomains: '1234'
});

var googleLayer = new L.Google("HYBRID");

var tileLayers = {
    'OpenStreetMap': osmLayer,
    'Open Aerial': openAerialLayer,
    'Google': googleLayer
};

L.control.layers(tileLayers).addTo(map);

var hash = new L.Hash(map);
var infotext =
    "<h3>NAMEHERE</h3><a href='//musicbrainz.org/place/MBIDHERE'>View this place on MusicBrainz</a>\
     <a href=\"COMMONSLINK\" target=\"_blank\">IMAGEHERE</a>";
var imageembed = "<img src=\"SOURCE\" alt=\"image of this place\"/>" //
$.getJSON("places.json").done(function(data){
var markerCluster = new L.MarkerClusterGroup();
var markers = [];
    $.each(data, function(key, val){
        mbid = key;
        name = val['name'];
        coordinates = val['coordinates']
        var marker = L.marker(coordinates, {'title': name});
        var text = infotext.replace("MBIDHERE", mbid);
        text = text.replace("NAMEHERE", name);
        if ('thumbnail_link' in val){
            text = text.replace("COMMONSLINK", val['commons_link'])
            text = text.replace("IMAGEHERE", imageembed.replace("SOURCE", val['thumbnail_link']))
        } else {
            text = text.replace("IMAGEHERE", "")
        }
        marker.bindPopup(text);
        markers.push(marker);
    });
    markerCluster.addLayers(markers);
    map.addLayer(markerCluster);
});
