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
        document.getElementById("messages").innerHTML = JSON.stringify(responseText["actionResponse"]);
    });
}

function refresh_whitelist_widget(msg) {
    $.ajax({
        url: "/protected/players/widgets/whitelist_widget",
        type: "GET",
        success: function(data) {
            document.getElementById('whitelist_status').innerHTML = data;
        }
    })
}
