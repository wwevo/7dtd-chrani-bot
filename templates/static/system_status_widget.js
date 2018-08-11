function bot_pause_resume(link_clicked, widget_id) {
    $.when(
        $.ajax({
            url: link_clicked.href,
            type: "GET",
            beforeSend: function(xhr){
                xhr.setRequestHeader("Content-Type","application/json");
                xhr.setRequestHeader('Accept', 'application/json');
            },
            success: function(data) {
                return data["actionResponse"];
            }
        }),
        $.ajax({
            url: "/protected/players/widgets/system_status_widget",
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

function refresh_system_status_widget() {
    $.ajax({
            url: "/protected/players/widgets/system_status_widget",
            type: "GET",
            success: function(data) {
                document.getElementById('bot_status').innerHTML = data;
                setTimeout(refresh_system_status_widget, 5000);
            }
        })
}

$(document).ready(function(){
    refresh_system_status_widget();
});
