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

function featureToPopup(feature){
    mbid = feature.key;
    name = feature.properties.name;
    coordinates = feature.properties.coordinates
    var marker = L.marker(coordinates, {'title': name});
    var info = document.createElement("div");

    var name = document.createElement("h3");
    name.textContent = feature.properties.name;
    info.appendChild(name);

    if ('thumbnail_link' in feature.properties){
        var imagelink = document.createElement("a");
        imagelink.href = feature.properties.commons_link
        imagelink.target = "_blank";

        var image = document.createElement("img");
        image.alt = "image of this place";
        image.src = feature.properties.thumbnail_link;

        imagelink.appendChild(image)

        info.appendChild(imagelink)
        info.appendChild(document.createElement("br"))

        var commonslink = document.createElement("a");
        commonslink.href = feature.properties.commons_link;
        commonslink.target = "_blank";
        info.appendChild(commonslink)
    }

    events = feature.properties.events
    if (events.length > 0){
        var heading = document.createElement("h4");
        heading.textContent = "Events";
        info.appendChild(heading);

        var ev_list = document.createElement("ul")
        $.each(events, function(index, event){
            var link = document.createElement("a");
            link.href = "//musicbrainz.org/event/" + event.gid;
            link.textContent = event.name;

            var li = document.createElement("li");
            li.appendChild(link);
            ev_list.appendChild(li);
        })
        info.appendChild(ev_list);
    }

    var link = document.createElement("a");
    link.href = "//musicbrainz.org/place/" + feature.id;
    link.textContent = "View this place on MusicBrainz";
    info.appendChild(link);
    return info;
}

var hash = new L.Hash(map);
$.getJSON("places.json").done(function(data){
    var markerCluster = new L.MarkerClusterGroup();
    var geoJsonLayer = L.geoJson(data, {
        onEachFeature: function(feature, layer) {
            layer.bindPopup(featureToPopup(feature));
        }
    });
    markerCluster.addLayer(geoJsonLayer);
    map.addLayer(markerCluster);
});
