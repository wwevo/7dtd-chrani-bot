function refresh_whitelist_widget(msg) {
    $.ajax({
        url: "/protected/players/widgets/system_whitelist_widget",
        type: "GET",
        success: function(data) {
            $('#whitelist_widget').html(data);
        }
    })
}
