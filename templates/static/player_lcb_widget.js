function refresh_player_lcb_widget(msg) {
    $.ajax({
        url: "/protected/players/widgets/player_lcb_widget/" + msg.steamid,
        type: "GET",
        success: function(data) {
            $('#plcbw_' + msg.steamid).replaceWith(data);
        }
    })
}
