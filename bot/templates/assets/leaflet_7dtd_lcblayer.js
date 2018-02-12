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

var lcb = pollLcb();
