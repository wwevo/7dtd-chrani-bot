$(document).ready(function(){
    //connect to the socket server.
    var socket = io.connect('http://' + document.domain + ':' + location.port + '/chrani-bot/public');

    socket.on('refresh_status', function(msg) {
        refresh_system_status_widget(msg)
    });

    socket.on('reinitialize', function(msg) {
        reload_page(msg)
    });

    socket.on('refresh_permissions', function(msg) {
        refresh_player_permissions_widget(msg)
    });

    socket.on('refresh_locations', function(msg) {
        refresh_player_locations_widget(msg)
    });

    socket.on('refresh_player_actions', function(msg) {
        refresh_player_actions_widget(msg)
    });

    socket.on('refresh_player_status', function(msg) {
        refresh_player_status_widget(msg)
    });

    socket.on('refresh_whitelist', function(msg) {
        refresh_whitelist_widget(msg)
    });

    socket.on('refresh_player_whitelist', function(msg) {
        refresh_player_whitelist_widget(msg)
        refresh_whitelist_widget(msg)
    });

    socket.on('remove_player_table_row', function(msg) {
        remove_player_table_row(msg)
    });

    socket.on('add_player_table_row', function(msg) {
        add_player_table_row(msg)
    });

    socket.on('update_player_table_row', function(msg) {
        update_player_table_row(msg)
    });

});