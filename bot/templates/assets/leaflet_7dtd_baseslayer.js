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

var bases = pollBases();
bases.addTo(map);