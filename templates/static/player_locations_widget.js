function refresh_player_locations_widget(msg) {
        $.ajax({
            url: "/protected/players/widgets/player_locations_widget/" + msg.steamid,
            type: "GET",
            success: function(data) {
                $('#plw_' + msg.entityid).html(data);
            }
        })
}

function player_action(link_clicked) {
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