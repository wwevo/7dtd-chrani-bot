function deepEqual(x, y) { // probably overkill
    const ok = Object.keys, tx = typeof x, ty = typeof y;
    return x && y && tx === 'object' && tx === ty ? (
            ok(x).length === ok(y).length &&
            ok(x).every(key => deepEqual(x[key], y[key]))
            ) : (x === y);
}

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
    var panel_user_steamid = document.getElementById("map").parentElement.id;

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
    setPlayerCenter(panel_user_steamid);
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
                });
    }
    updatePlayerTimeout = window.setTimeout(pollOnlinePlayers, 2000);
    return online_players;
};

function setPlayerCenter(steamid) {
    $.getJSON("/players/" + steamid)
            .done(function (data) {
                marker = createPlayerMarker(data[steamid]);
                online_players.addLayer(marker);
                map.setView(marker.getLatLng());
            });
};


function sortByKey(array, key) {
    return array.sort(function(a, b) {
        var x = a[key]; var y = b[key];
        return ((x < y) ? -1 : ((x > y) ? 1 : 0));
    });
}

var onlinePlayers = pollOnlinePlayers();
onlinePlayers.addTo(map);
