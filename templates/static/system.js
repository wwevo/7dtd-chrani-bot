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
        $('span.close').click(
            function() {
                $('#messages_modal').hide();
            }
        );

        $("body").click(function () {
            $("#messages_modal").fadeOut("fast");
        });

        $("main #player_table_widget").addClass("dominant");
        $("main #command_log_widget").addClass("wide");
        $("main #location_radar_widget").addClass("shamed").addClass("prominent");

        $(".switch_map_fullscreen").click(function () {
            $("main #player_table_widget").toggleClass("dominant").toggleClass("prominent");
            $("main #location_radar_widget").toggleClass("dominant").toggleClass("prominent").toggleClass("shamed");
            $("main #whitelist_widget").toggleClass("shamed");
            $("main #banned_players_widget").toggleClass("shamed");
            $("main #player_table_widget td:nth-child(2), main #player_table_widget th:nth-child(2)").toggle();
            $("main #player_table_widget td:nth-child(3), main #player_table_widget th:nth-child(3)").toggle();
            $("main #player_table_widget td:nth-child(4), main #player_table_widget th:nth-child(4)").toggleClass("tiny");
            $("main #player_table_widget td:nth-child(5), main #player_table_widget th:nth-child(5)").toggle();
            $("main #player_table_widget td:nth-child(6), main #player_table_widget th:nth-child(6)").toggle();
            $("main #player_table_widget td:nth-child(7), main #player_table_widget th:nth-child(7)").toggle();
            $("main #player_table_widget td:nth-child(8), main #player_table_widget th:nth-child(8)").toggle();
            if ($("main #location_radar_widget").hasClass("dominant")) {
                Cookies.set("map_fullscreen", true);
            } else {
                Cookies.remove("map_fullscreen");
            }
            resetSize(window.map);
        });

        init_radar();
        /*
         * This will directly affect output
         */
        $('#messages_modal').hide();
        if (Cookies.get("map_fullscreen")) {
            $("main #player_table_widget").removeClass("dominant").addClass("prominent");
            $("main #location_radar_widget").addClass("dominant").removeClass("prominent").removeClass("shamed");
            $("main #whitelist_widget").addClass("shamed");
            $("main #banned_players_widget").addClass("shamed");
            $("main #player_table_widget td:nth-child(2), main #player_table_widget th:nth-child(2)").hide();
            $("main #player_table_widget td:nth-child(3), main #player_table_widget th:nth-child(3)").hide();
            $("main #player_table_widget td:nth-child(4), main #player_table_widget th:nth-child(4)").addClass("tiny");
            $("main #player_table_widget td:nth-child(5), main #player_table_widget th:nth-child(5)").hide();
            $("main #player_table_widget td:nth-child(6), main #player_table_widget th:nth-child(6)").hide();
            $("main #player_table_widget td:nth-child(7), main #player_table_widget th:nth-child(7)").hide();
            $("main #player_table_widget td:nth-child(8), main #player_table_widget th:nth-child(8)").hide();
        }

        // These should come last so we have no flicker while rearranging stuff ^^
        resetSize(window.map);
    }
);

function showWebinterface() {
    $('#loading_screen').addClass("shamed");
    $('#flex_layout').removeClass("background");
}

function showLoadingScreen() {
    $('#loading_screen').removeClass("shamed");
    $('#flex_layout').addClass("background");
}
