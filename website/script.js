

// Create a new map centered on the continental US
var temp_map = L.map("temp_map").setView([47, 2], 6);
var clouds_map = L.map("clouds_map").setView([47, 2], 6);
var rain_map = L.map("rain_map").setView([47, 2], 6);

// Add OpenStreetMap to the map
var basemapUrl = "https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png";

L.tileLayer(basemapUrl).addTo(temp_map);
L.tileLayer(basemapUrl).addTo(clouds_map);
L.tileLayer(basemapUrl).addTo(rain_map);

// Add weather radar to the map
var corner1 = L.latLng(39.6, -8),
    corner2 = L.latLng(53.6, 12),
    bounds = L.latLngBounds(corner1, corner2);
temp_overlay = L.imageOverlay("weather_outputs/temp/image_0.png", bounds, { opacity: 0.5 }).addTo(temp_map);
clouds_overlay = L.imageOverlay("weather_outputs/clouds/image_0.png", bounds, { opacity: 0.5 }).addTo(clouds_map);
rain_overlay = L.imageOverlay("weather_outputs/rain/image_0.png", bounds, { opacity: 0.5 }).addTo(rain_map);

function showSlides(n) {
    temp_overlay.setUrl("weather_outputs/temp/image_"+n+".png");
    clouds_overlay.setUrl("weather_outputs/clouds/image_"+n+".png");
    rain_overlay.setUrl("weather_outputs/rain/image_"+n+".png");
}


