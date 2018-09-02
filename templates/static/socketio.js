$(document).ready(function(){
    //connect to the socket server.
    window.socket = io.connect('http://' + document.domain + ':' + location.port + '/chrani-bot/public');

    window.socket.on('refresh_status', function(msg) {
        refresh_system_status_widget(msg)
    });

    window.socket.on('reinitialize', function(msg) {
        reload_page(msg)
    });

    window.socket.on('refresh_permissions', function(msg) {
        refresh_player_permissions_widget(msg)
    });

    window.socket.on('refresh_locations', function(msg) {
        refresh_player_locations_widget(msg)
    });

    window.socket.on('refresh_player_actions', function(msg) {
        refresh_player_actions_widget(msg)
    });

    window.socket.on('refresh_player_status', function(msg) {
        refresh_player_status_widget(msg)
    });

    window.socket.on('refresh_whitelist', function(msg) {
        refresh_whitelist_widget(msg)
    });

    window.socket.on('refresh_player_whitelist', function(msg) {
        refresh_player_whitelist_widget(msg)
        refresh_whitelist_widget(msg)
    });

    window.socket.on('remove_player_table_row', function(msg) {
        remove_player_table_row(msg)
    });

    window.socket.on('add_player_table_row', function(msg) {
        add_player_table_row(msg)
    });

    window.socket.on('update_player_table_row', function(msg) {
        update_player_table_row(msg)
    });

    window.socket.on('refresh_player_table', function(msg) {
        refresh_player_table(msg)
    });

    window.socket.on('command_log', function(msg) {
        update_command_log(msg)
    });

    window.socket.on('leaflet_markers', function(msg) {
        setMarkers(msg);
    });

});