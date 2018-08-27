function update_player_status(msg) {
    $.ajax({
        url: "/protected/players/get_status/" + msg.steamid,
        type: "GET",
        beforeSend: function(xhr){
            xhr.setRequestHeader("Content-Type", "application/json");
            xhr.setRequestHeader('Accept', 'application/json');
        },
        success: function(data) {
            if (data["is_online"] == true) {
                $('#opw_' + msg.steamid).addClass("online");
                $('#opw_' + msg.steamid).prependTo('#player_table');
            } else {
                $('#opw_' + msg.steamid).removeClass("online")
                if (('.online')[0]) {
                    $('#opw_' + msg.steamid).insertAfter('#player_table > tbody:last-child');
                }
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
        url: "/protected/players/get_table_row/" + msg.steamid,
        type: "GET",
        success: function(data) {
            $('#player_table > tbody:last-child').after(data);
        }
    })
}

function remove_player_table_row(msg) {
    $('#opw_' + msg.steamid).fadeOut(600, function() {
        $(this).remove();
    });
}
