function alter_permission_group(link_clicked, steamid) {
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
        })
    ).then(function(responseText, html) {
        $('#messages').html(JSON.stringify(responseText["actionResponse"]));
    });
}

function refresh_player_permissions_widget(msg) {
        $.ajax({
            url: "/protected/players/widgets/player_permissions_widget/" + msg.steamid,
            type: "GET",
            success: function(data) {
                $('#ppw_' + msg.entityid).html(data);
            }
        })
}
