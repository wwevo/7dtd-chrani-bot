var panel_user_steamid = document.getElementById("map").parentElement.id;

function deepEqual(x, y) { // probably overkill
    const ok = Object.keys, tx = typeof x, ty = typeof y;
    return x && y && tx === 'object' && tx === ty ? (
            ok(x).length === ok(y).length &&
            ok(x).every(key => deepEqual(x[key], y[key]))
            ) : (x === y);
}
// <editor-fold defaultstate="collapsed" desc=" Base Markers ">
var basesMappingList = {};
var basesMappingListOld = {};
var active_bases = L.layerGroup();

function baseMarkerGetColor() {
    var color;
    color = 'green';
    return color;
}

function createBaseMarker(val) {
    var marker;
    var color;
    var bounds;

    bounds = [[Math.round(Number(val.pos_x)) - Math.round(Number(val.radius)), Math.round(Number(val.pos_z)) - Math.round(Number(val.radius))], [Math.round(Number(val.pos_x)) + Math.round(Number(val.radius)), Math.round(Number(val.pos_z)) + Math.round(Number(val.radius))]];
    baseid = val.owner;

    color = baseMarkerGetColor();
    marker = L.rectangle(bounds, {owner: val.owner, owner_steamid: val.owner, color: color, weight: 1, fillOpacity: 0.1});
    marker.bindTooltip(val.owner, {permanent: false, direction: "center"});
    marker.baseid = baseid;
    return marker;
}
// this shit is more of a mockup and not at all optimized or even thought through :)
// Let's get it to work first
var setBaseMarkers = function (data) {
    basesMappingListOld = jQuery.extend({}, basesMappingList);
    basesMappingList = {};
    var marker;
    var bases = 0;

    $.each(data, function (key, val) {
		marker = createBaseMarker(val)
        basesMappingList[val.owner] = {marker: marker, val: val};
    });
    if (jQuery.isEmptyObject(basesMappingListOld)) { // first run! 
        $.each(basesMappingList, function (key, val) {
            active_bases.addLayer(val.marker); // add all available bases
            bases++;
        });
    } else { // this only gets executed when the layer is active!
        // Now we want to remove the old markers...
        // Let's do it one by one. You can come up with a clever way later!
        active_bases.eachLayer(function (marker) {
            if (!basesMappingList.hasOwnProperty(marker.baseid)) { // it's not present in the current list!
                active_bases.removeLayer(marker); // remove
            } else { //  update the existing ones...
                if (!deepEqual(marker.getBounds(), basesMappingList[marker.baseid].marker.getBounds())) {
                    // moved base
                    marker.setBounds(basesMappingList[marker.baseid].marker.getBounds());
                }
                bases++;
            }
        });
        $.each(data, function (key, val) { // and add new ones!
			if (!basesMappingListOld.hasOwnProperty(val.owner)) {
				marker = createBaseMarker(val, '1st');
				basesMappingList[val.owner] = {marker: marker, val: val};
				active_bases.addLayer(marker); // add all available bases
				bases++;
			}
        });
    }
    $("#mapControlBasesCount").text(bases);
    return true;
};

var updateBasesTimeout = false;
var pollBases = function () {
    if (updateBasesTimeout === false // only false the very first time
            || map.hasLayer(active_bases)) { // only execute the poll if the layer is actually being displayed
        $.getJSON("/bases")
                .done(function (data) {
                    setBaseMarkers(data); // poll complete, set the markers!!
                });
    }
    updateBasesTimeout = window.setTimeout(pollBases, 7500); // if active or not, poll this function periodically
    return active_bases; // return current layer, this is just for convenience
};

// </editor-fold>
// <editor-fold defaultstate="collapsed" desc=" Player Markers and List ">
var playersMappingList = {};
var playersMappingListOld = {};
var online_players = L.layerGroup();

function createPlayerMarker(val) {
    var marker = L.marker([val.pos_x, val.pos_z], {title: val.name, steamid: val.steamid}).bindTooltip(val.name, {permanent: true, direction: "right"});
    marker.setOpacity(1.0);
    playersMappingList[val.steamid] = marker;
    marker.steamid = val.steamid;

    return marker;
}

var setOnlinePlayerMarkers = function (data) {
    playersMappingListOld = jQuery.extend({}, playersMappingList);
    playersMappingList = {};
    var marker;
    var online = 0;

    $.each(data, function (key, val) {
        marker = createPlayerMarker(val);
        playersMappingList[val.steamid] = {marker: marker, val: val};
    });
    if (jQuery.isEmptyObject(playersMappingListOld)) { // first run! 
        $.each(playersMappingList, function (key, val) {
            online_players.addLayer(val.marker); // add all available players
            online++;
        });
    } else { // this only gets executed when the layer is active!
        // Now we want to remove the old markers...
        // Let's do it one by one. You can come up with a clever way later!
        online_players.eachLayer(function (marker) {
            steamid = marker.steamid;
            if (!playersMappingList.hasOwnProperty(marker.steamid)) { // it's not present in the current list!
                online_players.removeLayer(marker); // remove
            } else { //  update the existing ones...
                if (!deepEqual(marker.getLatLng(), playersMappingList[marker.steamid].marker.getLatLng())) {
                    // moved player
                    var pos = L.latLng(playersMappingList[marker.steamid].val.pos_x, playersMappingList[marker.steamid].val.pos_z);
                    marker.setLatLng(pos).update(marker);
                }
                online++;
            }
        });
        $.each(data, function (key, val) { // and add new ones!
            if (!playersMappingListOld.hasOwnProperty(val.steamid)) {
                marker = createPlayerMarker(val);
                playersMappingList[val.steamid] = {marker: marker, val: val};
                online_players.addLayer(marker); // add all available bases
                online++;
            }
        });
    }
    $("#mapControlOnlineCount").text(online);
    return true;
};

var updatePlayerTimeout = false;
var pollOnlinePlayers = function () {
    if (updatePlayerTimeout === false
            || map.hasLayer(online_players)) {
        $.getJSON("/players/online")
                .done(function (data) {
                    setOnlinePlayerMarkers(data);
                    panel_user = playersMappingList[panel_user_steamid]
                    map.setView(panel_user.marker.getLatLng());
                });
    }
    updatePlayerTimeout = window.setTimeout(pollOnlinePlayers, 2000);
    return online_players;
};

function sortByKey(array, key) {
    return array.sort(function(a, b) {
        var x = a[key]; var y = b[key];
        return ((x < y) ? -1 : ((x > y) ? 1 : 0));
    });
}

// </editor-fold>
// <editor-fold defaultstate="collapsed" desc=" Location Markers and List ">
var locationsMappingList = {};
var locationsMappingListOld = {};
var active_locations = L.layerGroup();

function locationMarkerGetColor(protect) {
    var color;
    if (protect === '1') {
        color = 'green';
    } else {
        color = 'blue';
    }
    return color;
}

function createLocationMarker(val) {
    var marker;
    var color;
    var protect;
    var locationid;
    var bounds;

    bounds = [[Number(val.x) - Number(val.protectSize), Number(val.z) - Number(val.protectSize)], [Number(val.x) + Number(val.protectSize), Number(val.z) + Number(val.protectSize)]];
    color = locationMarkerGetColor(protect);
    marker = L.rectangle(bounds, {color: color, weight: 3, fillOpacity: 0, dashArray: "5 5 1 5"});
    marker.bindTooltip(val.name, {permanent: true, direction: "center"});
    locationid = val.name;
    protect = val.protect;

    marker.locationid = locationid;
    marker.protect = protect;
    return marker;
}
// this shit is more of a mockup and not at all optimized or even thought through :)
var setLocationMarkers = function (data) {
    locationsMappingListOld = jQuery.extend({}, locationsMappingList);
    locationsMappingList = {};
    var marker;
    var locations = 0;

    $.each(data, function (key, val) {
        locationsMappingList[val.name] = {marker: createLocationMarker(val), val: val};
    });
    if (jQuery.isEmptyObject(locationsMappingListOld)) { // first run! 
        $.each(locationsMappingList, function (key, val) {
            active_locations.addLayer(val.marker); // add all available bases
            locations++;
        });
    } else { // this only gets executed when the layer is active!
        // Now we want to remove the old markers...
        // Let's do it one by one. You can come up with a clever way later!
        active_locations.eachLayer(function (marker) {
            if (!locationsMappingList.hasOwnProperty(marker.locationid)) { // it's not present in the current list!
                active_locations.removeLayer(marker); // remove
            } else { //  update the existing ones...
                if (!deepEqual(marker.getBounds(), locationsMappingList[marker.locationid].marker.getBounds())) {
                    // moved base
                    marker.setBounds(locationsMappingList[marker.locationid].marker.getBounds());
                }
                if (marker.protect !== locationsMappingList[marker.locationid].marker.protect) {
                    // changed protection;
                    color = locationsMappingList[marker.locationid].marker.options.color;
                    marker.setStyle({color: color});
                    marker.protect = locationsMappingList[marker.locationid].marker.protect;
                }
                locations++;
            }
        });
        $.each(data, function (key, val) { // and add new ones!
                if (!locationsMappingListOld.hasOwnProperty(val.name)) {
                    marker = createLocationMarker(val);
                    locationsMappingList[val.name] = {marker: marker, val: val};
                    active_locations.addLayer(marker); // add all available bases
                    locations++;
                }
        });
    }
    $("#mapControlLocationsCount").text(locations);
    return true;
};

var updateLocationTimeout = false;
var pollLocations = function () {
    if (updateLocationTimeout === false // only false the very first time
            || map.hasLayer(active_locations)) { // only execute the poll if the layer is actually being displayed
        $.getJSON("/locations.php")
                .done(function (data) {
                    setLocationMarkers(data); // poll complete, set the markers!!
                });
    }
    updateLocationTimeout = window.setTimeout(pollLocations, 7500); // if active or not, poll this function periodically
    return active_locations; // return current layer, this is just for convenience
};

// </editor-fold>
// <editor-fold defaultstate="collapsed" desc=" LCB Markers ">
var lcbMappingList = {};
var active_lcb = L.layerGroup();

var setLcbMarkers = function (data) {
    active_lcb.clearLayers();
    lcbMappingList = {};
    var lcb = 0;
    $.each(data.claimowners, function (key, claimowners) {
        var marker;
        $.each(claimowners.claims, function (key, claim) {
            var bounds = [[Number(claim.x) - Number(data.claimsize / 2), Number(claim.z) - Number(data.claimsize / 2)], [Number(claim.x) + Number(data.claimsize / 2), Number(claim.z) + Number(data.claimsize / 2)]];
            if (claimowners.claimactive === true) {
                var color = 'green';
            } else {
                var color = 'red';
            }
            marker = L.rectangle(bounds, {color: color, weight: 1, fillOpacity: 0.1});
            marker.bindTooltip(claimowners.playername + " (claim)", {permanent: false, direction: "center"});

            active_lcb.addLayer(marker);
            lcbMappingList[lcb] = marker;
            lcb++;
        });
    });
    $("#mapControlLcbCount").text(lcb);
    return true;
};

var updateLcbTimeout = false;
var pollLcb = function () {
    if (updateLcbTimeout === false
            || map.hasLayer(active_lcb)) {
        $.getJSON("/landclaims.php")
                .done(function (data) {
                    setLcbMarkers(data);
                });
    }
    updateLcbTimeout = window.setTimeout(pollLcb, 60000);
    return active_lcb;
};
// </editor-fold>
// <editor-fold defaultstate="collapsed" desc=" Set up Game-Map ">
/*	create 7dtd map object
 utilizes Projection code from Allocs WebAndMapRendering */
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

    return new L.Map('map', {
        crs: SDTD_CRS,
        center: [0, 0],
        zoom: 5,
        zoomControl:false
    });
}
/*	fetch all map tiles and perform manual offset manipulation */
var updateTilelayerTimeout = false
function pollTileLayer() {
    var _tileLayer = L.tileLayer('/tiles/{z}/{x}/{y}.png', {
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

    updateTilelayerTimeout = window.setTimeout(pollTileLayer, 5000); // if active or not, poll this function periodically
    return _tileLayer;
}
// </editor-fold>
var map = initMap();

var tileLayer = pollTileLayer();
var onlinePlayers = pollOnlinePlayers();
var locations = pollLocations();
var bases = pollBases();
var lcb = pollLcb();

var baseMaps = {
    "World": tileLayer
};
var overlayMaps = {
    'Online players (<span id="mapControlOnlineCount">0</span>)': onlinePlayers,
    'All locations (<span id="mapControlLocationsCount">0</span>)': locations,
    'All bases (<span id="mapControlBasesCount">0</span>)': bases,
    'Landclaims (<span id="mapControlLcbCount">0</span>)': lcb
};

var overlayControl = L.control.layers(null, overlayMaps, {collapsed: false});

overlayControl.addTo(map);
tileLayer.addTo(map);
onlinePlayers.addTo(map);
locations.addTo(map);

map.dragging.disable();
map.touchZoom.disable();
map.doubleClickZoom.disable();
map.scrollWheelZoom.disable();
map.boxZoom.disable();
map.keyboard.disable();
if (map.tap) map.tap.disable();
document.getElementById('map').style.cursor='default';
