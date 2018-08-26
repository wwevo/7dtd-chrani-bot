function refresh_player_locations_widget(msg) {
    $.ajax({
        url: "/protected/players/widgets/player_locations_widget/" + msg.steamid,
        type: "GET",
        success: function(data) {
            $('#plw_' + msg.steamid).replaceWith(data);
        }
    })
}

$(document).ready(function() {
    $('ul[id^=plw_]').click(function() {
        $(this).find('ul').slideToggle()
    });
    $('ul[id^=plw_]').find('ul').hide()
});