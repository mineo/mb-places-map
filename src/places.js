var infotext = "<h3>NAMEHERE</h3><a href='//musicbrainz.org/place/MBIDHERE'>View this place on MusicBrainz</a>";

function makeMarker(map, mbid, data){
    name = data['name'];
    coordinates = data['coordinates'];
    var marker = new google.maps.Marker({
        position: new google.maps.LatLng(coordinates[0], coordinates[1]),
        title: name
    });
    marker.mbid = mbid;
    google.maps.event.addListener(marker, 'click', function(){
        text = infotext.replace("MBIDHERE", marker.mbid);
        text = text.replace("NAMEHERE", marker.title);
        var infowindow = new google.maps.InfoWindow({
            content: text
        });
        infowindow.open(map, marker);
    });
    return marker
}

function makeMap(){
    var mapOptions = {
        zoom: 4,
        center: new google.maps.LatLng(50.683889,10.919444),
        mapTypeId: google.maps.MapTypeId.ROADMAP
    };
    return new google.maps.Map(document.getElementById('map-canvas'), mapOptions);
}

function init(){
    map = makeMap();
    markers = [];
    $.getJSON("places.json").done(function(data){
        $.each(data, function(key, val){
            markers.push(makeMarker(map, key, val));
        });
        clusterOptions = {maxZoom:13};
        clusterer = new MarkerClusterer(map, markers, clusterOptions);
    });
}
