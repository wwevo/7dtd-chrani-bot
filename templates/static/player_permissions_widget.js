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
        document.getElementById("messages").innerHTML = JSON.stringify(responseText[0]);
    });
}

function refresh_player_permissions_widget(msg) {
        $.ajax({
            url: "/protected/players/widgets/permission_levels_widget/" + msg.steamid,
            type: "GET",
            success: function(data) {
                document.getElementById("ppw_" + msg.entityid).innerHTML = data;
            }
        })
}
