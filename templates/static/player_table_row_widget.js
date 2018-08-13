function update_player_table_row(msg) {
    $.ajax({
        url: "/protected/players/get_table_row/" + msg.steamid,
        type: "GET",
        success: function(data) {
            if ($('#opw_' + msg.steamid).length) {
                $('#opw_' + msg.steamid).replaceWith(data);
            } else {
                $('#player_table > tbody:last-child').after(data);
            }
        }
    })
}

function remove_player_table_row(msg) {
    $('#opw_' + msg.steamid).fadeOut(600, function() { $(this).remove(); });
}
