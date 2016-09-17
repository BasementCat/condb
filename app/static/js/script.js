var index_map;


function init_index_map() {
    var map_div = $('.home-index .map');
    if (!map_div.length) return;

    map_div.css({width: '100%', height: '10px'});
    map_div.css({height: map_div.innerWidth() * (2/3)});

    function make_markers() {
        $.get(
            '/api/conventions',
            function(data) {
                for (var i = 0; i < data.conventions.length; i++) {
                    var marker = new google.maps.Marker({
                        position: {
                            lat: data.conventions[i].location.latitude,
                            lng: data.conventions[i].location.longitude,
                        },
                        map: index_map,
                        title: data.conventions[i].convention.name,
                    });
                }
            },
            'json'
        );
    };

    function make_list() {
        $.get(
            '/api/conventions',
            function(data) {
                $('.home-index .convention-list-container')
                    .find('.convention')
                        .remove()
                    .end()
                    .append(data);
            },
            'html'
        );
    };

    function init(lat, lng) {
        index_map = new google.maps.Map(map_div[0], {
            center: {lat: lat, lng: lng},
            zoom: 8
        });

        make_markers();
        make_list();
    };

    function init_default() {
        init(38.6532137, -90.3135017);
    };

    if ("geolocation" in navigator) {
        navigator.geolocation.getCurrentPosition(
            function(position) {
                init(position.coords.latitude, position.coords.longitude);
            },
            init_default,
            {
                enableHighAccuracy: true,
                maximumAge        : 86400000,
                timeout           : 10000,
            }
        );
    } else {
        init_default();
    }
}
