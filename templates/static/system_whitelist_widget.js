function refresh_whitelist_widget(msg) {
    $.ajax({
        url: "/protected/players/widgets/system_whitelist_widget",
        type: "GET",
        success: function(data) {
            $('#whitelist_widget').html(data);
        }
    })
}

function refresh_player_whitelist_widget(msg) {
    $.ajax({
        url: "/protected/players/widgets/player_whitelist_widget/" + msg.steamid,
        type: "GET",
        success: function(data) {
            $('#pww_' + msg.steamid).replaceWith(data);
        }
    })
}