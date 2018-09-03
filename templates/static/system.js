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

function update_command_log(msg) {
    $('#command_log_widget #command_log').prepend(msg['steamid'] + "/" + msg['command'] + "<br/>");
}

$(document).ready(
    function() {
        // $('#widgets').hide();
        $('#messages_modal').hide();
        $('span.close').click(
            function() {
                $('#messages_modal').hide();
            }
        );

        $("body").click(function () {
            $("#messages_modal").fadeOut("fast");
        });

        init_radar();

        $(".switch_fullscreen").click(function () {
            $("main #command_log_widget").animate({visibility: 'toggle'});
        });

        $(".switch_map_fullscreen").click(function () {
            $("main #player_table_widget").toggleClass("dominant").toggleClass("prominent");
            $("main #player_location_radar_widget").toggleClass("dominant").toggleClass("prominent").toggleClass("shamed");
            $("main #system_whitelist_widget").toggleClass("shamed");
            $("main #system_banned_players_widget").toggleClass("shamed");
            $("main #player_table_widget td:nth-child(2), main #player_table_widget th:nth-child(2)").toggle();
            $("main #player_table_widget td:nth-child(3), main #player_table_widget th:nth-child(3)").toggle();
            $("main #player_table_widget td:nth-child(4), main #player_table_widget th:nth-child(4)").toggle();
            $("main #player_table_widget td:nth-child(5), main #player_table_widget th:nth-child(5)").toggle();
            $("main #player_table_widget td:nth-child(6), main #player_table_widget th:nth-child(6)").toggle();
            $("main #player_table_widget td:nth-child(7), main #player_table_widget th:nth-child(7)").toggle();
            resetSize(window.map);
        });
    }
);
