var panel_user_steamid = document.getElementById("map").parentElement.id;
/*	create 7dtd map object
 utilizes Projection code from Allocs WebAndMapRendering */
function initMap() {
    SDTD_Projection = {
        project: function (latlng) {
            return new L.Point(
                    (latlng.lat) / Math.pow(2, 4),
                    (latlng.lng) / Math.pow(2, 4));
        },
        unproject: function (point) {
            return new L.LatLng(
                    point.x * Math.pow(2, 4),
                    point.y * Math.pow(2, 4));
        }
    };

    SDTD_CRS = L.extend({}, L.CRS.Simple, {
        projection: SDTD_Projection,
        transformation: new L.Transformation(1, 0, -1, 0),
        scale: function (zoom) {
            return Math.pow(2, zoom);
        }
    });

    return new L.Map('map', {
        crs: SDTD_CRS,
        center: [0, 0],
        zoom: 5,
        zoomControl:false
    });
}

/*	fetch all map tiles and perform manual offset manipulation */
function pollTileLayer() {
    var _tileLayer = L.tileLayer('/tiles/{z}/{x}/{y}.png', {
        tileSize: 128,
        minNativeZoom: 0,
        minZoom: -1,
        maxNativeZoom: 4,
        maxZoom: 7,
        attribution: 'Tiles Courtesy of <a href="http://7daystodie.com/" target="_blank">7DtD</a>'
    });
    /*	Small hack to be able to use the weird tile-layout 7dtd provides
     thanks goes out to IvanSanchez and ghybs from stackexchange.
     */
    _tileLayer.getTileUrl = function (coords) {
        coords.y = (-coords.y) - 1;
        return L.TileLayer.prototype.getTileUrl.bind(_tileLayer)(coords);
    };

    return _tileLayer;
}

var map = initMap();

var tileLayer = pollTileLayer();

tileLayer.addTo(map);
map.dragging.disable();
map.touchZoom.disable();
map.doubleClickZoom.disable();
map.scrollWheelZoom.disable();
map.boxZoom.disable();
map.keyboard.disable();
if (map.tap) map.tap.disable();
document.getElementById('map').style.cursor='default';
