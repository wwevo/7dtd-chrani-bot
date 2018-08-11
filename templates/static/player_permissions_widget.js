function alter_permission_group(link_clicked, steamid, widget_id) {
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
        $.ajax({
            url: "/protected/players/widgets/permission_levels_widget/" + steamid,
            type: "GET",
            success: function(data) {
                return data;
            }
        })
    ).then(function(responseText, html) {
        document.getElementById("messages").innerHTML = JSON.stringify(responseText[0]);
        document.getElementById(widget_id).innerHTML = html[0];
    });
}
