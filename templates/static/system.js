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
        $('#messages_modal .modal-body').html(JSON.stringify(responseText["actionResponse"]));
        $('#messages_modal').show();
    });
}

function send_form(form_submitted) {
    $.when(
        $.ajax({
            url: form_submitted.action,
            type: 'POST',
            dataType: 'json',
            data: $(form_submitted).serialize(),
            success: function(data) {
                return data["actionResponse"];
            },
            error: function(jqXHR, textStatus, errorThrown) {
                 alert(textStatus + " " + errorThrown);
            }
        }),
    ).then(function(responseText, html) {
        $('#messages_modal .modal-body').html(JSON.stringify(responseText["actionResponse"]));
        $('#messages_modal').show();
    });
}

function reload_page() {
    setTimeout( function(){
        location.reload(true)
    }, 1000);
}

$(document).ready(
    function() {
        $('#widgets').hide();
        $('#messages_modal').hide();
        $('span.close').click(
            function() {
                $('#messages_modal').hide();
            }
        );

        $("body").click(function () {
            $("#messages_modal").fadeOut("fast");
        });

        $(".switch_fullscreen").click(function () {
            $("#widgets").animate({visibility: 'toggle'});
        });
    }
);
