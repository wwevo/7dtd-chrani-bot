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
                markers[obj.id] = new L.circle(xy(obj.pos_x, obj.pos_z), {weight: 1, color: 'orange', radius: obj.radius});
                markers[obj.id].bindTooltip(obj.identifier + "<br />" + obj.owner, { permanent: true });
                if (obj.protected) {
                    markers[obj.id + "_inner"] = new L.circle(xy(obj.pos_x, obj.pos_z), {weight: 1, color: 'red', radius: obj.inner_radius});
                } else {
                    markers[obj.id + "_inner"] = new L.circle(xy(obj.pos_x, obj.pos_z), {weight: 0, color: 'blue', radius: obj.inner_radius});
                }
                markers[obj.id + "_inner"].addTo(window.map);
            } else {
                markers[obj.id] = new L.marker(xy(obj.pos_x, obj.pos_z));
                if (obj.online) {
                    markers[obj.id].bindTooltip(obj.identifier + "<br />" + obj.owner, { permanent: true });
                } else {
                    markers[obj.id].bindTooltip(obj.identifier + "<br />" + obj.owner, { permanent: false });
                }
            }
            markers[obj.id].addTo(window.map);
        } else {
            // Set new latlng on marker
            markers[obj.id].setLatLng(xy(obj.pos_x, obj.pos_z));
            if (obj.type == "circle") {
                markers[obj.id + "_inner"].setLatLng(xy(obj.pos_x, obj.pos_z));
                if (obj.protected) {
                    markers[obj.id + "_inner"].setStyle({weight: 1, color: 'red'});
                } else {
                    markers[obj.id + "_inner"].setStyle({wight: 0, color: 'blue'});
                }
            } else {
                if (obj.online) {
                    markers[obj.id].openTooltip();
                } else {
                    markers[obj.id].closeTooltip();
                }
            }
        }
    });
}

function removeMarkers(data) {
    data.forEach(function (obj) {
        // Check if there is already a marker with that id in the markers object
        if (markers.hasOwnProperty(obj.id)) {
            if (obj.type == "circle") {
                window.map.removeLayer(markers[obj.id]);
                window.map.removeLayer(markers[obj.id + "_inner"]);
                delete markers[obj.id + "_inner"];
            } else {
                window.map.removeLayer(markers[obj.id]);
            }
            delete markers[obj.id];
        }
    });
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

function center_canvas_on(id) {
    window.map.panTo(markers[id].getLatLng());
}
