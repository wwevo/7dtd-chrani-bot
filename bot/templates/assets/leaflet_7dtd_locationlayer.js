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

var locations = pollLocations();
