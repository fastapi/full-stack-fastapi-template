import React, { useEffect, useRef } from "react";
import {
  MapContainer,
  GeoJSON,
  TileLayer,
  LayersControl,
  Marker,
  Popup,
  ScaleControl,
  ZoomControl,
} from "react-leaflet";
import L, { Map, LatLngTuple } from "leaflet"; // Import Leaflet for map and layers handling
import "./leaflet.css"; // Import CSS for the map styling
import markerIconPng from "./icons/placeholder.png"; // Import a custom marker icon for the map

// Define initial map center coordinates with explicit type LatLngTuple
const center: LatLngTuple = [51.505, -0.09];

// Define a custom marker icon for the map
const icon = new L.Icon({
  iconUrl: markerIconPng, // Path to the icon image
  iconSize: [25, 41], // Size of the icon
  iconAnchor: [12, 41], // Position of the icon anchor point (bottom of the icon)
  popupAnchor: [1, -34], // Popup anchor relative to the icon
  shadowSize: [41, 41], // Size of the shadow for the marker icon
});

interface LeafletMapComponentProps {
  geojson: any; // GeoJSON data passed to the component to display on the map
}

// LeafletMapComponent renders a Leaflet map with custom layers and geoJSON data
const LeafletMapComponent: React.FC<LeafletMapComponentProps> = ({ geojson }) => {
  const mapRef = useRef<Map | null>(null); // Reference to store the map instance with Map type

  // useEffect hook to handle geoJSON data updates and adjust map bounds
  useEffect(() => {
    console.log("LeafletMapComponent: geojson received", geojson);

    if (geojson && mapRef.current) {
      const map = mapRef.current;
      const geojsonLayer = L.geoJSON(geojson); // Create a geoJSON layer from the received data
      const bounds = geojsonLayer.getBounds(); // Get the bounding box of the geoJSON layer

      console.log("GeoJSON Bounds:", bounds);

      // Adjust map bounds to fit the geoJSON data on the map
      if (bounds.isValid()) {
        map.fitBounds(bounds);
      } else {
        console.error("Invalid bounds:", bounds);
      }
    }
  }, [geojson]); // Only runs when the geojson data changes

  // Function to define what happens when each feature in the geoJSON layer is interacted with
  const onEachFeature = (feature: any, layer: L.Layer) => {
    if (feature.properties) {
      layer.bindPopup(
        Object.keys(feature.properties)
          .map((k) => `${k}: ${feature.properties[k]}`)
          .join("<br />"),
        {
          maxHeight: 200, // Maximum height for the popup
        }
      );
    }
  };

  return (
    // MapContainer initializes the Leaflet map container
    <MapContainer
      center={center} // Center of the map (from the `center` constant)
      zoom={13} // Initial zoom level
      className="leaflet-container" // Apply custom CSS styles to the map container
      zoomControl={false} // Disable default zoom controls, use custom ones below
      ref={(mapInstance) => {
        if (mapInstance && !mapRef.current) {
          mapRef.current = mapInstance; // Store map instance in ref once created
        }
      }}
    >
      <LayersControl position="topright">
        {/* LayersControl to manage different map layers */}
        <LayersControl.BaseLayer checked name="OSM">
          <TileLayer
            attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
            url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
          />
        </LayersControl.BaseLayer>
        <LayersControl.BaseLayer name="Satellite Hybrid">
          <TileLayer
            attribution='&copy; CNES, Distribution Airbus DS, © Airbus DS, © PlanetObserver (Contains Copernicus Data) | &copy; <a href="https://www.stadiamaps.com/" target="_blank">Stadia Maps</a> &copy; <a href="https://openmaptiles.org/" target="_blank">OpenMapTiles</a> &copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
            url="https://tiles.stadiamaps.com/tiles/alidade_satellite/{z}/{x}/{y}.jpg"
          />
        </LayersControl.BaseLayer>
      </LayersControl>

      {/* Render the geoJSON layer if geojson data is available */}
      {geojson && <GeoJSON data={geojson} onEachFeature={onEachFeature} />}

      {/* Render a custom marker at the center position */}
      <Marker position={center} icon={icon}>
        <Popup>A simple popup.</Popup> {/* Popup content for the marker */}
      </Marker>

      {/* Add a scale control to the map */}
      <ScaleControl position="bottomright" maxWidth={300} metric={true} imperial={false} />

      {/* Add zoom control to the bottom left corner */}
      <ZoomControl position="bottomleft" />
    </MapContainer>
  );
};

export default LeafletMapComponent;