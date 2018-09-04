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

// https://gis.stackexchange.com/a/206498
PlayerOnlineIcon = L.icon({
    iconUrl: 'static/icons/leaflet/player_online.png',
    iconSize: [10, 19]
});

PlayerOfflineIcon = L.icon({
    iconUrl: 'static/icons/leaflet/player_offline.png',
    iconSize: [10, 19]
});

// https://stackoverflow.com/a/32737982/8967590
var markers = {};
var layers = {};
var active_controls = [];

// Function for setting/updating markers
function setMarkers(data) {
    data.forEach(function (obj) {
        // Check if there is already a marker with that id in the markers object
        if (!markers.hasOwnProperty(obj.id)) {
            if (!layers.hasOwnProperty(obj.layerGroup)) {
                layers[obj.layerGroup] = L.layerGroup();
            }
            if (obj.type == "circle") {
                markers[obj.id] = new L.circle(xy(obj.pos_x, obj.pos_z), {weight: 1, color: 'green', radius: obj.radius});
                markers[obj.id].bindTooltip(obj.identifier + "<br />" + obj.owner_name, { permanent: false });
                if (obj.protected) {
                    markers[obj.id + "_inner"] = new L.circle(xy(obj.pos_x, obj.pos_z), {weight: 1, color: 'red', radius: obj.inner_radius});
                } else {
                    markers[obj.id + "_inner"] = new L.circle(xy(obj.pos_x, obj.pos_z), {weight: 0, color: 'darkgreen', radius: obj.inner_radius});
                }
                layers[obj.layerGroup].addLayer(markers[obj.id + "_inner"]);
            } else {
                markers[obj.id] = new L.marker(xy(obj.pos_x, obj.pos_z), {icon: PlayerOfflineIcon});
                if (obj.online) {
                    markers[obj.id].bindTooltip(obj.name, { permanent: true });
                    markers[obj.id].setIcon(PlayerOnlineIcon)
                } else {
                    markers[obj.id].bindTooltip(obj.name, { permanent: false });
                    markers[obj.id].setIcon(PlayerOfflineIcon)
                }
            }
            layers[obj.layerGroup].addLayer(markers[obj.id]);
        } else {
            // Set new latlng on marker
            markers[obj.id].setLatLng(xy(obj.pos_x, obj.pos_z));
            if (obj.type == "circle") {
                markers[obj.id].setRadius(obj.radius);
                markers[obj.id + "_inner"].setLatLng(xy(obj.pos_x, obj.pos_z));
                markers[obj.id + "_inner"].setRadius(obj.inner_radius);
                if (obj.protected) {
                    markers[obj.id + "_inner"].setStyle({weight: 1, color: 'red'});
                } else {
                    markers[obj.id + "_inner"].setStyle({weight: 0, color: 'blue'});
                }
            } else {
                if (obj.online) {
                    markers[obj.id].openTooltip();
                    markers[obj.id].setIcon(PlayerOnlineIcon);
                } else {
                    markers[obj.id].closeTooltip();
                    markers[obj.id].setIcon(PlayerOfflineIcon);
                }
            }
        }
    });
    for (var layerGroup in layers) {
        if (layers.hasOwnProperty(layerGroup)) {
            if(typeof active_controls[layerGroup] === 'undefined') {
                window.control.addOverlay(layers[layerGroup], layerGroup);
                active_controls[layerGroup] = true;
            }
        }
    }
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

	var bounds = [xy(-10000, -10000), xy(10000, 10000)];
    var image = L.imageOverlay('uqm_map_full.png', bounds).addTo(window.map);
    resetSize(window.map);
	window.map.setView(xy(0, 0), map.getZoom());
    window.control = L.control.layers(null, null, {collapsed: false}).addTo(window.map);

    window.socket.emit('initiate_leaflet', {data: true});
}

function center_canvas_on(id) {
    window.map.panTo(markers[id].getLatLng());
}
