function refresh_player_status_widget(msg) {
    $.ajax({
        url: "/protected/players/widgets/player_status_widget/" + msg.steamid,
        type: "GET",
        success: function(data) {
            $('#psw_' + msg.steamid).replaceWith(data);
        }
    })
}
