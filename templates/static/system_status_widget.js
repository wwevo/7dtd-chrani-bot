function bot_pause_resume(link_clicked, widget_id) {
    $.when(
        $.ajax({
            url: link_clicked.href,
            type: "GET",
            beforeSend: function(xhr){
                xhr.setRequestHeader("Content-Type", "application/json");
                xhr.setRequestHeader('Accept', 'application/json');
            },
            success: function(data) {
                return data["actionResponse"];
            }
        }),
    ).then(function(responseText, html) {
        $('#messages').html(JSON.stringify(responseText["actionResponse"]));
    });
}

function refresh_system_status_widget(msg) {
    $.ajax({
        url: "/protected/players/widgets/system_status_widget",
        type: "GET",
        success: function(data) {
            $('#bot_status').html(data);
        }
    })
}
