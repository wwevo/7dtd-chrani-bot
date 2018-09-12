function refresh_player_whitelist_widget(msg) {
    $.ajax({
        url: "/protected/players/widgets/player_whitelist_widget/" + msg.steamid,
        type: "GET",
        success: function(data) {
            $('#pww_' + msg.steamid).replaceWith(data);
        }
    })
}