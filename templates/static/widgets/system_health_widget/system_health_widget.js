function refresh_system_health_widget(msg) {
    $.ajax({
        url: "/protected/players/widgets/system_health_widget",
        type: "GET",
        success: function(data) {
            $('#bot_health').html(data);
        }
    })
}
