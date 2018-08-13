function refresh_player_locations_widget(msg) {
        $.ajax({
            url: "/protected/players/widgets/player_locations_widget/" + msg.steamid,
            type: "GET",
            success: function(data) {
                $('#plw_' + msg.entityid).html(data);
            }
        })
}
