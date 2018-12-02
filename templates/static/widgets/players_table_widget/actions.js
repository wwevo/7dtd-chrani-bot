function refresh_player_actions_widget(msg) {
    $.ajax({
        url: "/protected/players/widgets/player_actions_widget/" + msg.steamid,
        type: "GET",
        success: function(data) {
            $('#paw_' + msg.steamid).replaceWith(data);
        }
    })
}
