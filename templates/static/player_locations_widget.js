function refresh_player_locations_widget(msg) {
    $.ajax({
        url: "/protected/players/widgets/player_locations_widget/" + msg.steamid,
        type: "GET",
        success: function(data) {
            $('#plw_' + msg.steamid).replaceWith(data);
        }
    })
}

function get_locations() {
    $.ajax({
        url: "/protected/players/player_locations",
        type: "GET",
        beforeSend: function(xhr){
            xhr.setRequestHeader("Content-Type", "application/json");
            xhr.setRequestHeader('Accept', 'application/json');
        },
        success: function(data) {
            init_radar(data);
        }
    });
}


function init_radar(data) {
    var canvas = document.getElementById('location_radar')
    var ctx = canvas.getContext('2d');
    var control = new CanvasManipulation(
        canvas
        , function() { draw(ctx, data) }
        , {leftTop: {x: -10000, y: -10000}, rightBottom: {x: 10000, y: 10000}}
    )
    control.init();
    control.layout();
    draw(ctx, data);
}


function draw(ctx, data) {
    ctx.clearCanvas();
    var i = 0;
    if (data) while (data[i]) {
        ctx.beginPath();
        ctx.arc(data[i]["pos_x"], data[i]["pos_z"], data[i]["radius"], 0, 2 * Math.PI);
        ctx.lineWidth = 1;
        ctx.strokeStyle = "#0000ff";
        ctx.stroke();
        ctx.font = "12px Arial";
        ctx.fillText(data[i]["identifier"], data[i]["pos_x"], data[i]["pos_z"]);
        i++;
    }
}
