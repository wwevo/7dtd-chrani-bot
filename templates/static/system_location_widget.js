var yx = L.latLng;
var xy = function(x, y) {
    if (L.Util.isArray(x)) {    // When doing xy([x, y]);
        return yx(x[1], x[0]);
    }
    return yx(y, x);  // When doing xy(x, y);
};

var resetSize = function(map) {
    var height = $("#player_location_radar_widget").height() - $("#player_location_radar_widget table thead").height();
    var width = $("#player_location_radar_widget").width();
    $("#location_radar").height(height).width(width);
    map.invalidateSize();
    return true;
}

// https://stackoverflow.com/a/32737982/8967590
var markers = {};

// Function for setting/updating markers
function setMarkers(data) {
    data.forEach(function (obj) {
        // Check if there is already a marker with that id in the markers object
        if (!markers.hasOwnProperty(obj.id)) {
            if (obj.type == "circle") {
                markers[obj.id] = new L.circle(xy(obj.pos_x, obj.pos_z), {radius: obj.radius});
                markers[obj.id].bindTooltip(obj.identifier + "<br />" + obj.owner, { permanent: true });
            } else {
                markers[obj.id] = new L.marker(xy(obj.pos_x, obj.pos_z));
                markers[obj.id].bindTooltip(obj.identifier + "<br />" + obj.owner, { permanent: false });
            }
            markers[obj.id].addTo(window.map);
            markers[obj.id].previousLatLngs = [];
        } else {
            // Store the previous latlng
            markers[obj.id].previousLatLngs.push(markers[obj.id].getLatLng());
            markers[obj.id].previousLatLngs = markers[obj.id].previousLatLngs.slice(0, 10);
            // Set new latlng on marker
            markers[obj.id].setLatLng(xy(obj.pos_x, obj.pos_z));
        }
    });
    resetSize(window.map);
	window.map.setView(xy(0, 0), map.getZoom());
}

function init_radar() {
    window.map = L.map('location_radar', {
        crs: L.CRS.Simple,
        minZoom: -10,
        maxZoom: 4,
        zoom: -3,
    });

    window.map.on("move", function() {});
    window.map.on("moveend", function() {});
    window.map.on('zoomend', function() {
        var currentZoom = map.getZoom();
        if (currentZoom >= 0) {}
    });

	var bounds = [xy(-10000, -10000), xy(10000, 10000)];
    var image = L.imageOverlay('uqm_map_full.png', bounds).addTo(window.map);
    resetSize(window.map);
	window.map.setView(xy(0, 0), map.getZoom());
}

function center_canvas_on(pos_x, pos_z) {
    window.map.panTo(xy(pos_x, pos_z));
}
