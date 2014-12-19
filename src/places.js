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
var imageembed = "\
    <a href=\"COMMONSLINK\" target=\"_blank\"><img src=\"SOURCE\" alt=\"image of this place\"/></a>\
    <br/>\
    <a href=\"COMMONSLINK\" target=\"_blank\">Image from Wikimedia Commons</a>";
$.getJSON("places.json").done(function(data){
var markerCluster = new L.MarkerClusterGroup();
var markers = [];
    $.each(data, function(key, val){
        mbid = key;
        name = val['name'];
        coordinates = val['coordinates']
        var marker = L.marker(coordinates, {'title': name});
        var info = document.createElement("div");

        var name = document.createElement("h3");
        name.textContent = val.name;
        info.appendChild(name);

        // info.appendChild(document.createElement("br"))

        if ('thumbnail_link' in val){
            var imagelink = document.createElement("a");
            imagelink.href = val.commons_link
            imagelink.target = "_blank";

            var image = document.createElement("img");
            image.alt = "image of this place";
            image.src = val.thumbnail_link;

            imagelink.appendChild(image)

            info.appendChild(imagelink)
            info.appendChild(document.createElement("br"))

            var commonslink = document.createElement("a");
            commonslink.href = val.commons_link;
            commonslink.target = "_blank";
            info.appendChild(commonslink)
        }
        var link = document.createElement("a");
        link.href = "//musicbrainz.org/place/" + key;
        link.textContent = "View this place on MusicBrainz";
        info.appendChild(link);

        marker.bindPopup(info);
        markers.push(marker);
    });
    markerCluster.addLayers(markers);
    map.addLayer(markerCluster);
});
