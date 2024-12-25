fetch("https://ipinfo.io/json?token=45a0b01f8664a2")
    .then((response) => response.json())
    .then((jsonResponse) => {
        console.log(jsonResponse);

        // Convert `loc` string to a list of integers
        let coordinates = jsonResponse.loc.split(',').map(coord => parseFloat(coord));

        // Initialize the map
        let map = L.map('map').setView(coordinates, 8);
        L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', {
            maxZoom: 19,
            attribution: '&copy; <a href="http://www.openstreetmap.org/copyright">OpenStreetMap</a>'
        }).addTo(map);

        // Add a marker to the map
        L.marker(coordinates).addTo(map)
            .bindPopup(`${jsonResponse.city}, ${jsonResponse.region}.`)
            .openPopup();

        // Add a click listener for the map
        var popup = L.popup();

        function onMapClick(e) {
            popup
            .setLatLng(e.latlng)
            .setContent("You clicked the map at " + e.latlng.toString())
            .openOn(map);
        }

        map.on('click', onMapClick);
    })
    .catch((error) => {
        console.error("Error fetching data:", error);
    });
