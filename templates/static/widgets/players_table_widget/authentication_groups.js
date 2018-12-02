function refresh_player_permissions_widget(msg) {
    $.ajax({
        url: "/protected/players/widgets/player_permissions_widget/" + msg.steamid,
        type: "GET",
        success: function(data) {
            $('#ppw_' + msg.steamid).replaceWith(data);
        }
    })
}
