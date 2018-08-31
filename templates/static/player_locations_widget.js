function refresh_player_locations_widget(msg) {
    $.ajax({
        url: "/protected/players/widgets/player_locations_widget/" + msg.steamid,
        type: "GET",
        success: function(data) {
            $('#plw_' + msg.steamid).replaceWith(data);
        }
    })
}

function get_locations() {
    $.ajax({
        url: "/protected/players/player_locations",
        type: "GET",
        beforeSend: function(xhr){
            xhr.setRequestHeader("Content-Type", "application/json");
            xhr.setRequestHeader('Accept', 'application/json');
        },
        success: function(data) {
            init_radar(data);
        }
    });
}

    var yx = L.latLng;
    var xy = function(x, y) {
        if (L.Util.isArray(x)) {    // When doing xy([x, y]);
            return yx(x[1], x[0]);
        }
        return yx(y, x);  // When doing xy(x, y);
    };


function init_radar(data) {
    window.map = L.map('location_radar', {
        crs: L.CRS.Simple,
        minZoom: -4
    });

	var bounds = [xy(-10000, -10000), xy(10000, 10000)];
    var image = L.imageOverlay('uqm_map_full.png', bounds).addTo(window.map);

    var i = 0;
    if (data) while (data[i]) {
        marker = L.circle(xy(data[i]["pos_x"], data[i]["pos_z"]), {radius: data[i]["radius"]});
        marker.bindTooltip(data[i]["identifier"], { permanent: true });
        marker.addTo(window.map);
        i++;
    }

    $("#location_radar").height($("#player_location_radar_widget").height()).width($("#player_location_radar_widget").width());
    window.map.invalidateSize();
	window.map.setView(xy(0, 0), 1);
}

function center_canvas_on(pos_x, pos_z) {
    window.map.panTo(xy(pos_x, pos_z));
}