function refresh_scheduler_status_widget(msg) {
    $.ajax({
        url: "/protected/system/widgets/get_scheduler_status_widget/" + msg.scheduler_name,
        type: "GET",
        success: function(data) {
            $('#ssw_' + msg.scheduler_name).replaceWith(data);
        }
    })
}