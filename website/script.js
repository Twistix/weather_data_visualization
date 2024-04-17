/* Variables */
var current_image = "image_0.png"

var temp_time = document.getElementById("temp_time");
var temp_map = L.map("temp_map");

var clouds_time = document.getElementById("clouds_time");
var clouds_map = L.map("clouds_map").setView([47, 2], 6);

var rain_time = document.getElementById("rain_time");
var rain_map = L.map("rain_map").setView([47, 2], 6);

var basemapUrl = "https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png";
var corner1 = L.latLng(40, -8);
var corner2 = L.latLng(54, 12);
var bounds = L.latLngBounds(corner1, corner2);


/* Init time text */
update_time_text(temp_time, "temp", current_image);
update_time_text(clouds_time, "clouds", current_image);
update_time_text(rain_time, "rain", current_image);


/* Init weather maps */
/* Set initial view */
temp_map.setView([47, 2], 6);
clouds_map.setView([47, 2], 6);
rain_map.setView([47, 2], 6);

/* Add OpenStreetMap background */
L.tileLayer(basemapUrl).addTo(temp_map);
L.tileLayer(basemapUrl).addTo(clouds_map);
L.tileLayer(basemapUrl).addTo(rain_map);

/* Add weather radar to the map */
temp_overlay = L.imageOverlay("./weather_outputs/temp/"+current_image, bounds, { opacity: 0.5 }).addTo(temp_map);
clouds_overlay = L.imageOverlay("./weather_outputs/clouds/"+current_image, bounds, { opacity: 0.5 }).addTo(clouds_map);
rain_overlay = L.imageOverlay("./weather_outputs/rain/"+current_image, bounds, { opacity: 0.5 }).addTo(rain_map);


/* Functions */
function showSlides(n) {
    /* Update image names */
    current_image = "image_"+n+".png";

    /* Update time text */
    update_time_text(temp_time, "temp", current_image);
    update_time_text(clouds_time, "clouds", current_image);
    update_time_text(rain_time, "rain", current_image);

    /* Update overlays */
    temp_overlay.setUrl("./weather_outputs/temp/"+current_image);
    clouds_overlay.setUrl("./weather_outputs/clouds/"+current_image);
    rain_overlay.setUrl("./weather_outputs/rain/"+current_image);
}

async function update_time_text(time_element, data_type, data_image) {
    var response = await fetch("./weather_outputs/"+data_type+"/image_properties.json");
    var json = await response.json();
    time_element.textContent = json[data_image].time;
}