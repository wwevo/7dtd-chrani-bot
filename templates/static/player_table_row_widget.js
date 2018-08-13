function update_player_table_row(msg) {
    $.ajax({
        url: "/protected/players/get_table_row/" + msg.steamid,
        type: "GET",
        success: function(data) {
            if ($('#opw_' + msg.entityid).length) {
                $('#opw_' + msg.entityid).replaceWith(data);
            } else {
                $('#player_table > tbody:last-child').after(data);
            }
        }
    })
}

function remove_player_table_row(msg) {
    $('#opw_' + msg.entityid).fadeOut(600, function() { $(this).remove(); });
}
