import React from 'react';
import { LayersControl, TileLayer } from 'react-leaflet';

const basemaps = {
  OpenStreetMap: {
    name: "OpenStreetMap",
    url: "https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png",
    attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
  },
  GoogleSatellite: {
    name: "Google Satellite",
    url: "http://{s}.google.com/vt/lyrs=s&x={x}&y={y}&z={z}",
    attribution: '&copy; <a href="https://www.google.com/maps">Google Maps</a>',
    subdomains: ['mt0', 'mt1', 'mt2', 'mt3']
  },
  GoogleTerrain: {
    name: "Google Terrain",
    url: "http://{s}.google.com/vt/lyrs=p&x={x}&y={y}&z={z}",
    attribution: '&copy; <a href="https://www.google.com/maps">Google Maps</a>',
    subdomains: ['mt0', 'mt1', 'mt2', 'mt3']
  },
  GoogleHybrid: {
    name: "Google Hybrid",
    url: "http://{s}.google.com/vt/lyrs=y&x={x}&y={y}&z={z}",
    attribution: '&copy; <a href="https://www.google.com/maps">Google Maps</a>',
    subdomains: ['mt0', 'mt1', 'mt2', 'mt3']
  }
};

const MapSwitcher = () => {
  return (
    <LayersControl position="bottomright">
      {Object.keys(basemaps).map((key, index) => (
        <LayersControl.BaseLayer key={index} name={basemaps[key].name} checked={index === 0}>
          <TileLayer
            attribution={basemaps[key].attribution}
            url={basemaps[key].url}
            subdomains={basemaps[key].subdomains}
          />
        </LayersControl.BaseLayer>
      ))}
    </LayersControl>
  );
};

export default MapSwitcher;