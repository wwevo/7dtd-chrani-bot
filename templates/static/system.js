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

function update_system_log(msg) {
    $('#system_log_widget #' + msg['type'] + '_log').prepend("(" + msg['type'] + ")" + msg['steamid'] + "/" + msg['command'] + "<br/>");
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
        $("main .widget").removeClass("dominant").removeClass("prominent").removeClass("shamed").removeClass("full");
        if (Cookies.get("page") == "map")  {
            init_radar();
            $("main .widget").removeClass("wide");
            $("main #player_table_widget").addClass("prominent").removeClass("dominant");
            $("main #location_radar_widget").addClass("dominant");
            $("main #system_log_widget").addClass("wide");
            // These should come last so we have no flicker while rearranging stuff ^^
            resetSize(window.map);
        } else if (Cookies.get("page") == "settings")  {
            $("main .widget").removeClass("wide");
            $("main #settings_scheduler_widget").addClass("wide");
            $("main #settings_player_observer_widget").addClass("wide");
            $("main #system_log_widget").addClass("wide");
            $("main #location_radar_widget").addClass("shamed");
        } else {
            $("main .widget").removeClass("wide").addClass("shamed");
            $("main #player_table_widget").addClass("dominant").removeClass("prominent").removeClass("shamed");
            $("main #system_log_widget").addClass("wide").removeClass("shamed");
            $("main #whitelist_widget").removeClass("shamed");
            $("main #banned_players_widget").removeClass("shamed");
            $("main #location_radar_widget").addClass("shamed");
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
