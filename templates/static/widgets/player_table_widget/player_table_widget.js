function refresh_player_table(msg) {
    $.ajax({
        url: "/protected/players/widgets/get_player_table_widget",
        type: "GET",
        success: function(data) {
            $('#player_table_widget').html(data);
        }
    })
}

function update_player_status(msg) {
    $.ajax({
        url: "/protected/players/get_status/" + msg.steamid,
        type: "GET",
        beforeSend: function(xhr){
            xhr.setRequestHeader("Content-Type", "application/json");
            xhr.setRequestHeader('Accept', 'application/json');
        },
        success: function(data) {
            if (data["is_logging_in"] == true) {
                $('#opw_' + msg.steamid).addClass("connecting");
                $('#opw_' + msg.steamid).removeClass("offline");
                $('#opw_' + msg.steamid).removeClass("online");
                $('#opw_' + msg.steamid).appendTo('#player_table_widget > table');
            } else if (data["is_online"] == true) {
                $('#opw_' + msg.steamid).addClass("online");
                $('#opw_' + msg.steamid).removeClass("connecting");
                $('#opw_' + msg.steamid).removeClass("offline");
                $('#opw_' + msg.steamid).prependTo('#player_table_widget > table');
            } else {
                $('#opw_' + msg.steamid).addClass("offline");
                $('#opw_' + msg.steamid).removeClass("online");
                $('#opw_' + msg.steamid).removeClass("connecting");
                $('#opw_' + msg.steamid).appendTo('#player_table_widget > table');
            }
            refresh_player_actions_widget(msg);
        }
    });
}

function update_player_table_row(msg) {
    if ($('#opw_' + msg.steamid).length) {
        refresh_player_whitelist_widget(msg);
        refresh_player_locations_widget(msg);
        refresh_player_lcb_widget(msg);
        refresh_player_permissions_widget(msg);
        refresh_player_status_widget(msg);
        update_player_status(msg);
    } else {
        add_player_table_row(msg);
    }
}

function add_player_table_row(msg) {
    $.ajax({
        url: "/protected/players/get_player_table_row/" + msg.steamid,
        type: "GET",
        success: function(data) {
            $('#player_table_widget > table > tbody:last-child').after(data);
            if ($("main #player_table_widget").hasClass("prominent")) {
                $("main #player_table_widget td:nth-child(2), main #player_table_widget th:nth-child(2)").hide();
                $("main #player_table_widget td:nth-child(3), main #player_table_widget th:nth-child(3)").hide();
                $("main #player_table_widget td:nth-child(4), main #player_table_widget th:nth-child(4)").addClass("tiny");
                $("main #player_table_widget td:nth-child(5), main #player_table_widget th:nth-child(5)").hide();
                $("main #player_table_widget td:nth-child(6), main #player_table_widget th:nth-child(6)").hide();
                $("main #player_table_widget td:nth-child(7), main #player_table_widget th:nth-child(7)").hide();
                $("main #player_table_widget td:nth-child(8), main #player_table_widget th:nth-child(8)").hide();
            }
        }
    })
}

function remove_player_table_row(msg) {
    $('#opw_' + msg.steamid).fadeOut(600, function() {
        $(this).remove();
    });
}
