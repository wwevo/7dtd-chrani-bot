$(document).ready(function(){
    //connect to the socket server.
    var socket = io.connect('http://' + document.domain + ':' + location.port + '/test');

    socket.on('refresh_status', function(msg) {
        refresh_system_status_widget(msg)
    });

    socket.on('refresh_permissions', function(msg) {
        refresh_player_permissions_widget(msg)
    });

    socket.on('refresh_locations', function(msg) {
        refresh_player_locations_widget(msg)
    });

    socket.on('refresh_whitelist', function(msg) {
        refresh_whitelist_widget(msg)
    });

    socket.on('remove_player_table_row', function(msg) {
        remove_player_table_row(msg)
    });

});