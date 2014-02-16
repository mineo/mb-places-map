var map = L.map('map-canvas').setView([50.683889,10.919444], 4);
L.tileLayer('http://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: 'Map data &copy; <a href="http://openstreetmap.org">OpenStreetMap</a> contributors.',
    maxZoom: 19
}).addTo(map);
var hash = new L.Hash(map);
var infotext =
    "<h3>NAMEHERE</h3><a href='//musicbrainz.org/place/MBIDHERE'>View this place on MusicBrainz</a>";
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
        marker.bindPopup(text);
        markers.push(marker);
    });
    markerCluster.addLayers(markers);
    map.addLayer(markerCluster);
});
