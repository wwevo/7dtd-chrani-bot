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

function send_form(form_submitted) {
    $.when(
        $.ajax({
            url: form_submitted.action,
            type: 'post',
            dataType: 'json',
            data: $(form_submitted).serialize(),
            success: function(data) {
                return data["actionResponse"];
            }
        }),
    ).then(function(responseText, html) {
        $('#messages').html(JSON.stringify(responseText["actionResponse"]));
    });
}

function reload_page() {
    setTimeout( function(){
        location.reload(true)
    }, 1000);
}