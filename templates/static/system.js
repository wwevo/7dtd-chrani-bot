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
    $('#command_log_widget #command_log').prepend("(" + msg['type'] + ")" + msg['steamid'] + "/" + msg['command'] + "<br/>");
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

        $(".switch_players_fullscreen").click(function () {
            Cookies.set("page", "players");
            reload_page();
        });

        $(".switch_map_fullscreen").click(function () {
            Cookies.set("page", "map");
            reload_page();
        });

        $(".switch_settings_fullscreen").click(function () {
            Cookies.set("page", "settings");
            reload_page();
        });

        /*
         * This will directly affect output
         */
        $('#messages_modal').hide();

        if (Cookies.get("page") == "map")  {
            init_radar();
            $("main #player_table_widget").addClass("prominent").removeClass("dominant");
            $("main #location_radar_widget").addClass("dominant");
            $("main #status_log_widget").addClass("wide");
            // These should come last so we have no flicker while rearranging stuff ^^
            resetSize(window.map);
        }
        if (Cookies.get("page") == "settings")  {
            $("main #settings_scheduler_widget").addClass("wide");
            $("main #settings_player_observer_widget").addClass("wide");
            $("main #command_log_widget").addClass("wide");
        }
        if (Cookies.get("page") == "players")  {
            $("main #player_table_widget").addClass("dominant").removeClass("prominent");
            $("main #status_log_widget").addClass("wide");
        }
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
