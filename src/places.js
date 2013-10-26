function init(){
    var map = new OpenLayers.Map({
        div: "map-canvas",
    });
    var osm = new OpenLayers.Layer.OSM("OSM");
    var gmap = new OpenLayers.Layer.Google("Google", {
        type: google.maps.MapTypeId.ROADMAP,
        numZoomLevels: 22
    });
    var gmap_sat = new OpenLayers.Layer.Google("Google Satellite", {
        type: google.maps.MapTypeId.HYBRID,
        numZoomLevels: 22
    });
    var markers = new OpenLayers.Layer.Markers("Places");
    var projection = new OpenLayers.Projection("EPSG:4326");
    var infotext =
        "<a href='//musicbrainz.org/place/MBIDHERE'>View this place on MusicBrainz</a>";

    map.addLayers([osm, gmap, gmap_sat, markers]);
    map.addControl(new OpenLayers.Control.LayerSwitcher());
    var ilmenau = new OpenLayers.LonLat(10.919444,50.683889).transform(
            projection,
            map.getProjectionObject()
    );
    $.getJSON("places.json").done(function(data){
        $.each(data, function(key, val){
            mbid = key;
            name = val.name;
            coordinates = val.coordinates;
            var marker = new OpenLayers.Marker(
                new OpenLayers.LonLat(coordinates[1], coordinates[0]).transform(
                    projection,
                    map.getProjectionObject()
            ));
            marker.mbid = mbid;
            markers.addMarker(marker);
        });
    });
    map.setCenter(
        ilmenau,
        4
    );
}
$(window).load(init);
