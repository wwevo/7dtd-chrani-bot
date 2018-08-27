function refresh_player_locations_widget(msg) {
    $.ajax({
        url: "/protected/players/widgets/player_locations_widget/" + msg.steamid,
        type: "GET",
        success: function(data) {
            $('#plw_' + msg.steamid).replaceWith(data);
        }
    })
}

/*
$(document).ready(function() {
    $('[id^=plw_] select').change(function() {
        var option = this.options[this.selectedIndex];
        $(this).closest("select").attr("class", $(option).attr("class"));
    });
});
*/
