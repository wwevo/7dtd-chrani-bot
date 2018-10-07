var resetSize = function(map) {
    var height = $("#location_radar_widget").height() - $("#location_radar_widget table thead").height();
    var width = $("#location_radar_widget").width();
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

function createCircleMarker(obj) {
    bounds = [obj.pos_x, obj.pos_z]
    markers[obj.id] = new L.circle(bounds, {weight: 1, color: 'green', radius: Number(obj.radius / Math.pow(2, 4))});
    markers[obj.id].bindTooltip(obj.identifier + "<br />" + obj.owner_name, { permanent: false });
    if (obj.protected) {
        markers[obj.id + "_inner"] = new L.circle(bounds, {weight: 1, color: 'red', radius: Number(obj.inner_radius / Math.pow(2, 4))});
    } else {
        markers[obj.id + "_inner"] = new L.circle(bounds, {weight: 0, color: 'darkgreen', radius: Number(obj.inner_radius / Math.pow(2, 4))});
    }
    layers[obj.layerGroup].addLayer(markers[obj.id]);
    layers[obj.layerGroup].addLayer(markers[obj.id + "_inner"]);
}

function createRectangleMarker(obj) {
    bounds = [[obj.pos_x - obj.radius, obj.pos_z - obj.radius], [obj.pos_x + obj.radius, obj.pos_z + obj.radius]]
    markers[obj.id] = new L.rectangle(bounds, {weight: 1, color: 'green'});

    markers[obj.id].bindTooltip(obj.identifier + "<br />" + obj.owner_name, { permanent: false });
    if (obj.protected) {
        markers[obj.id + "_inner"] = new L.rectangle(bounds, {weight: 1, color: 'red'});
    } else {
        markers[obj.id + "_inner"] = new L.rectangle(bounds, {weight: 1, color: 'darkgreen'});
    }
    layers[obj.layerGroup].addLayer(markers[obj.id]);
    layers[obj.layerGroup].addLayer(markers[obj.id + "_inner"]);
}

function createStandardMarker(obj) {
    markers[obj.id] = new L.marker([obj.pos_x, obj.pos_z], {icon: PlayerOfflineIcon});
    if (obj.online) {
        markers[obj.id].bindTooltip(obj.name, { permanent: true });
        markers[obj.id].setIcon(PlayerOnlineIcon)
    } else {
        markers[obj.id].bindTooltip(obj.name, { permanent: false });
        markers[obj.id].setIcon(PlayerOfflineIcon)
    }
    layers[obj.layerGroup].addLayer(markers[obj.id]);
}

function removeGeometricMarker(obj) {
    if (markers[obj.id] != undefined) {
        map.removeLayer(markers[obj.id]);
    }
    if (markers[obj.id + "_inner"] != undefined) {
        map.removeLayer(markers[obj.id + "_inner"]);
    }
}

// Function for setting/updating markers
function setMarkers(data) {
    data.forEach(function (obj) {
        // Check if there is already a marker with that id in the markers object
        if (!markers.hasOwnProperty(obj.id)) {
            if (!layers.hasOwnProperty(obj.layerGroup)) {
                layers[obj.layerGroup] = L.layerGroup();
            }
            if (obj.type == "circle" || obj.type == "sphere") {
                createCircleMarker(obj);
            } else if (obj.type == "square" || obj.type == "cube") {
                createRectangleMarker(obj);
            } else {
                createStandardMarker(obj);
            }
        } else {
            // Set new latlng on marker
            if (obj.type == "circle" || obj.type == "sphere") {
                if (!markers[obj.id].hasOwnProperty('setRadius')) {
                    removeGeometricMarker(obj);
                    createCircleMarker(obj);
                } else {
                    markers[obj.id].setLatLng([obj.pos_x, obj.pos_z]);
                    markers[obj.id].setRadius(obj.radius);
                    markers[obj.id + "_inner"].setLatLng([obj.pos_x, obj.pos_z]);
                    markers[obj.id + "_inner"].setRadius(obj.inner_radius);
                    if (obj.protected) {
                        markers[obj.id + "_inner"].setStyle({weight: 1, color: 'red'});
                    } else {
                        markers[obj.id + "_inner"].setStyle({weight: 0, color: 'blue'});
                    }
                }
            } else if (obj.type == "square" || obj.type == "cube") {
                if (!markers[obj.id].hasOwnProperty('setLatLng')) {
                    removeGeometricMarker(obj);
                    createRectangleMarker(obj);
                } else {
                    bounds = [[obj.pos_x - obj.radius / 2, obj.pos_z - obj.radius / 2], [obj.pos_x + obj.radius / 2, obj.pos_z + obj.radius / 2]]
                    markers[obj.id].setBounds(bounds);
                    bounds = [[obj.pos_x - obj.inner_radius / 2, obj.pos_z - obj.inner_radius / 2], [obj.pos_x + obj.inner_radius / 2, obj.pos_z + obj.inner_radius / 2]]
                    markers[obj.id + "_inner"].setBounds(bounds);
                }
            } else {
                markers[obj.id].setLatLng([obj.pos_x, obj.pos_z]);
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
                if (Cookies.get(layerGroup)) {
                    layers[layerGroup].addTo(window.map);
                }
                active_controls[layerGroup] = true;
            }
        }
    }
}

function removeMarkers(data) {
    data.forEach(function (obj) {
        // Check if there is already a marker with that id in the markers object
        if (markers.hasOwnProperty(obj.id)) {
            if (obj.type == "circle" || obj.type == "square") {
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

function initMap() {
    SDTD_Projection = {
        project: function (latlng) {
            return new L.Point(
                    (latlng.lat) / Math.pow(2, 4),
                    (latlng.lng) / Math.pow(2, 4));
        },
        unproject: function (point) {
            return new L.LatLng(
                    point.x * Math.pow(2, 4),
                    point.y * Math.pow(2, 4));
        }
    };

    SDTD_CRS = L.extend({}, L.CRS.Simple, {
        projection: SDTD_Projection,
        transformation: new L.Transformation(1, 0, -1, 0),
        scale: function (zoom) {
            return Math.pow(2, zoom);
        }
    });

    return new L.Map('location_radar', {
        crs: SDTD_CRS,
        center: [0, -0],
        zoom: 2
    });
}

/*	fetch all map tiles and perform manual offset manipulation */
function pollTileLayer() {
    var _tileLayer = L.tileLayer(allocs_webmap_tilelayer, {
        tileSize: 128,
        minNativeZoom: 0,
        minZoom: -1,
        maxNativeZoom: 4,
        maxZoom: 7,
        attribution: 'Tiles Courtesy of <a href="http://7daystodie.com/" target="_blank">7DtD</a>'
    });
    /*	Small hack to be able to use the weird tile-layout 7dtd provides
     thanks goes out to IvanSanchez and ghybs from stackexchange.
     */
    _tileLayer.getTileUrl = function (coords) {
        coords.y = (-coords.y) - 1;
        return L.TileLayer.prototype.getTileUrl.bind(_tileLayer)(coords);
    };
    return _tileLayer;
}
// </editor-fold>
function init_radar() {
    window.map = initMap();
    window.tileLayer = pollTileLayer();

    window.map.on('overlayadd', function(overlay) {
        Cookies.set(overlay.name, true);
    });
    window.map.on('overlayremove', function(overlay) {
        Cookies.remove(overlay.name);
    });
    resetSize(window.map);

    window.tileLayer.addTo(window.map);
	window.map.setView([0, 0], map.getZoom());
    window.control = L.control.layers(null, null, {collapsed: false}).addTo(window.map);

    window.socket.emit('initiate_leaflet', {data: true});
}

function center_canvas_on_marker(id) {
    window.map.panTo(markers[id].getLatLng());
}

function center_canvas_on_coords(pos_x, pos_z) {
    window.map.panTo([pos_x, pos_z]);
}