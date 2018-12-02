function refresh_whitelist_widget(msg) {
    $.ajax({
        url: "/protected/system/widgets/whitelist_general_widget",
        type: "GET",
        success: function(data) {
            $('#whitelist_widget').html(data);
        }
    })
}
