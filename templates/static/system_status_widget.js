function refresh_system_status_widget(msg) {
    $.ajax({
        url: "/protected/players/widgets/system_status_widget",
        type: "GET",
        success: function(data) {
            $('#bot_status').html(data);
        }
    })
}
