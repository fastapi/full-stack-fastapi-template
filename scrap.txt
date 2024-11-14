import React, { useEffect } from "react";
import {
  MapContainer,
  TileLayer,
  LayersControl,
  GeoJSON,
  ScaleControl,
  ZoomControl,
  useMap,
} from "react-leaflet";
import L, { LatLngTuple } from "leaflet"; // Explicit import of Leaflet
import "leaflet/dist/leaflet.css"; // Ensure Leaflet CSS is imported

const center: LatLngTuple = [51.505, -0.09];

interface LeafletMapComponentProps {
  geojson: any;
}

// Hook to adjust map bounds when geoJSON changes
function FitBounds({ geojson }: { geojson: any }) {
  const map = useMap(); // This hook provides access to the map instance

  useEffect(() => {
    if (geojson && map) {
      const geojsonLayer = L.geoJSON(geojson); // Add geoJSON to the map
      const bounds = geojsonLayer.getBounds(); // Get the bounds of the geoJSON layer

      if (bounds.isValid()) {
        map.fitBounds(bounds); // Fit the map to the geoJSON layer bounds
      }
    }
  }, [geojson, map]); // Re-run when geojson or map changes

  return null;
}

const LeafletMapComponent: React.FC<LeafletMapComponentProps> = ({ geojson }) => {
  return (
    <MapContainer
      center={center}
      zoom={13}
      className="leaflet-container"
      style={{ height: "100%", width: "100%" }}
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
      {geojson && <GeoJSON data={geojson} />}

      {/* Fit bounds based on geoJSON */}
      <FitBounds geojson={geojson} />

      {/* Add a scale control to the map */}
      <ScaleControl position="bottomright" maxWidth={300} metric={true} imperial={false} />

      {/* Add zoom control to the bottom left corner */}
      <ZoomControl position="bottomleft" />
    </MapContainer>
  );
};

export default LeafletMapComponent;