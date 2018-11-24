function refresh_player_observer_status_widget(msg) {
    $.ajax({
        url: "/protected/system/widgets/get_player_observer_status_widget/" + msg.player_observer_name,
        type: "GET",
        success: function(data) {
            $('#pocw_' + msg.player_observer_name).replaceWith(data);
        }
    })
}