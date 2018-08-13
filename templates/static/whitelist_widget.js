function whitelist_pause_resume(link_clicked, widget_id) {
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

function refresh_whitelist_widget(msg) {
    $.ajax({
        url: "/protected/players/widgets/whitelist_widget",
        type: "GET",
        success: function(data) {
            $('#whitelist_status').html(data);
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