"use client";

import React, { useState, useEffect } from "react";
import {
  ComposableMap,
  Geographies,
  Geography,
  Marker,
  Line,
  ZoomableGroup
} from "react-simple-maps";
import { ShieldAlert, Handshake, TrendingUp, AlertTriangle } from "lucide-react";

const geoUrl = "https://cdn.jsdelivr.net/npm/world-atlas@2/countries-110m.json";

const INITIAL_MARKERS = [
  { id: "ukraine", name: "Kyiv, Ukraine", type: "CONFLICT", coordinates: [30.5234, 50.4501], desc: "Active regional conflict and defensive operations." },
  { id: "russia", name: "Moscow, Russia", type: "CONFLICT", coordinates: [37.6173, 55.7558], desc: "Origin point of military deployment." },
  { id: "gaza", name: "Gaza / Israel", type: "CONFLICT", coordinates: [34.4668, 31.5017], desc: "High-intensity localized conflict and humanitarian crisis." },
  { id: "us_dc", name: "Washington DC, USA", type: "DIPLOMACY", coordinates: [-77.0369, 38.9072], desc: "Providing diplomatic and strategic support." },
  { id: "eu_brussels", name: "Brussels, EU", type: "DIPLOMACY", coordinates: [4.3517, 50.8503], desc: "NATO/EU coordination and sanctions command." },
  { id: "china_bj", name: "Beijing, China", type: "TRADE", coordinates: [116.4074, 39.9042], desc: "Major trade corridor and geopolitical balancing." },
  { id: "taiwan", name: "Taipei, Taiwan", type: "CONFLICT", coordinates: [121.5654, 25.0330], desc: "Elevated geopolitical tension and maritime monitoring." },
  { id: "turkey", name: "Anatolia, Turkey", type: "DISASTER", coordinates: [35.2433, 38.9637], desc: "Ongoing recovery from major seismic events." },
];

const INITIAL_CONNECTIONS = [
  { from: "russia", to: "ukraine", type: "CONFLICT" },
  { from: "us_dc", to: "ukraine", type: "DIPLOMACY" },
  { from: "eu_brussels", to: "ukraine", type: "DIPLOMACY" },
  { from: "us_dc", to: "gaza", type: "DIPLOMACY" },
  { from: "us_dc", to: "taiwan", type: "DIPLOMACY" },
  { from: "china_bj", to: "taiwan", type: "CONFLICT" },
  { from: "us_dc", to: "china_bj", type: "TRADE" },
  { from: "eu_brussels", to: "turkey", type: "DISASTER" },
];

const TYPE_STYLES = {
  CONFLICT: { color: "#DC3545", icon: ShieldAlert, label: "CONFLICT" },
  DIPLOMACY: { color: "#0056B3", icon: Handshake, label: "DIPLOMACY" },
  TRADE: { color: "#28A745", icon: TrendingUp, label: "TRADE" },
  DISASTER: { color: "#FD7E14", icon: AlertTriangle, label: "DISASTER" },
};

export function GeoNetworkMap() {
  const [markers, setMarkers] = useState(INITIAL_MARKERS);
  const [connections, setConnections] = useState(INITIAL_CONNECTIONS);
  const [activeFilters, setActiveFilters] = useState({
    CONFLICT: true,
    DIPLOMACY: true,
    TRADE: true,
    DISASTER: true,
  });

  const [hoveredNode, setHoveredNode] = useState<string | null>(null);
  const [tooltip, setTooltip] = useState<{ x: number; y: number; data: any } | null>(null);

  useEffect(() => {
    const interval = setInterval(async () => {
      try {
        const response = await fetch("/api/intelligence/stream");
        if (!response.ok) throw new Error("Stream unavailable");
        const data = await response.json();
        setMarkers(data.markers);
        setConnections(data.connections);
      } catch (error) {
        setMarkers(prev => 
          prev.map(m => {
            if (Math.random() > 0.8) {
              return {
                ...m,
                coordinates: [
                  m.coordinates[0] + (Math.random() - 0.5) * 0.5,
                  m.coordinates[1] + (Math.random() - 0.5) * 0.5
                ]
              };
            }
            return m;
          })
        );
      }
    }, 1000);

    return () => clearInterval(interval);
  }, []);

  const toggleFilter = (type: string) => {
    setActiveFilters((prev: any) => ({ ...prev, [type]: !prev[type] }));
  };

  const visibleMarkers = markers.filter((m) => activeFilters[m.type as keyof typeof activeFilters]);

  const visibleConnections = connections.filter(
    (c) =>
      (c.from === hoveredNode || c.to === hoveredNode) &&
      activeFilters[markers.find(m => m.id === c.from)?.type as keyof typeof activeFilters] &&
      activeFilters[markers.find(m => m.id === c.to)?.type as keyof typeof activeFilters]
  );

  return (
    <div className="relative w-full h-[700px] bg-slate-50 border border-slate-200 rounded-md shadow-sm overflow-hidden flex flex-col font-sans">
      
      {/* Tier 1 / Header Ribbon */}
      <div className="bg-[#152A38] text-white px-6 py-3 flex justify-between items-center z-10 border-b-2 border-b-[#FF9933]">
        <h2 className="text-lg font-bold tracking-wide">Global Event Topology</h2>
        <div className="flex items-center gap-3">
          <span className="relative flex h-3 w-3">
            <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-red-400 opacity-75"></span>
            <span className="relative inline-flex rounded-full h-3 w-3 bg-red-500"></span>
          </span>
          <button className="bg-blue-600 hover:bg-blue-700 text-sm px-4 py-1.5 rounded transition-colors font-medium">
            Live Intelligence
          </button>
        </div>
      </div>

      {/* Main Map Canvas */}
      <div className="flex-1 w-full h-full relative">
        <ComposableMap projection="geoMercator" projectionConfig={{ scale: 130 }} className="w-full h-full outline-none">
          <ZoomableGroup center={[10, 20]} zoom={1} maxZoom={4}>
            {/* Render Geography */}
            <Geographies geography={geoUrl}>
              {({ geographies }) =>
                geographies.map((geo) => (
                  <Geography
                    key={geo.rsmKey}
                    geography={geo}
                    fill="#e2e8f0" 
                    stroke="#cbd5e1" 
                    strokeWidth={0.5}
                    style={{
                      default: { outline: "none" },
                      hover: { fill: "#cbd5e1", outline: "none" },
                      pressed: { outline: "none" },
                    }}
                  />
                ))
              }
            </Geographies>

            {/* Render Arcs (Connections) */}
            {visibleConnections.map((conn, idx) => {
              const fromMarker = markers.find((m) => m.id === conn.from);
              const toMarker = markers.find((m) => m.id === conn.to);
              if (!fromMarker || !toMarker) return null;

              return (
                <Line
                  key={`line-${idx}`}
                  from={fromMarker.coordinates as [number, number]}
                  to={toMarker.coordinates as [number, number]}
                  stroke={TYPE_STYLES[conn.type as keyof typeof TYPE_STYLES].color}
                  strokeWidth={2}
                  strokeLinecap="round"
                  style={{ opacity: 0.6, strokeDasharray: "4 4" }}
                />
              );
            })}

            {/* Render Markers */}
            {visibleMarkers.map((marker) => {
              const isActiveNode = hoveredNode === marker.id;
              // To prevent react re-renders from closing tooltip, we check if hovered node ID matches
              return (
                <Marker
                  key={marker.id}
                  coordinates={marker.coordinates as [number, number]}
                  onMouseEnter={(e) => {
                    setHoveredNode(marker.id);
                    setTooltip({
                      x: e.clientX,
                      y: e.clientY,
                      data: marker,
                    });
                  }}
                  onMouseLeave={() => {
                    setHoveredNode(null);
                    setTooltip(null);
                  }}
                  onMouseMove={(e) => {
                    if (isActiveNode) {
                      setTooltip({
                        x: e.clientX,
                        y: e.clientY,
                        data: marker,
                      });
                    }
                  }}
                  style={{ cursor: "pointer" }}
                >
                  <circle
                    r={isActiveNode ? 8 : 5}
                    fill={TYPE_STYLES[marker.type as keyof typeof TYPE_STYLES].color}
                    stroke="#ffffff"
                    strokeWidth={2}
                    className="transition-all duration-200"
                  />
                </Marker>
              );
            })}
          </ZoomableGroup>
        </ComposableMap>
      </div>

      {/* Legend & Filters (Bottom Left) */}
      <div className="absolute bottom-6 left-6 bg-white p-4 rounded-md shadow-md border border-slate-200 z-20 w-48">
        <h3 className="text-xs font-bold text-slate-500 mb-3 tracking-wider uppercase">Event Filters</h3>
        <div className="flex flex-col space-y-2">
          {Object.entries(TYPE_STYLES).map(([key, style]) => {
            const isActive = activeFilters[key as keyof typeof activeFilters];
            return (
              <label key={key} className="flex items-center space-x-3 cursor-pointer group">
                <input
                  type="checkbox"
                  checked={isActive}
                  onChange={() => toggleFilter(key)}
                  className="w-4 h-4 rounded border-slate-300 text-blue-600 focus:ring-blue-500 cursor-pointer"
                />
                <span
                  className="w-3 h-3 rounded-full"
                  style={{ backgroundColor: isActive ? style.color : "#cbd5e1" }}
                />
                <span className={`text-sm font-medium ${isActive ? 'text-slate-800' : 'text-slate-400'}`}>
                  {style.label}
                </span>
              </label>
            );
          })}
        </div>
      </div>

      {/* Hover Tooltip Popover */}
      {tooltip && tooltip.data && (
        <div
          className="fixed bg-white border border-slate-200 shadow-xl rounded-md p-3 z-50 pointer-events-none w-64"
          style={{ top: tooltip.y + 15, left: tooltip.x + 15 }}
        >
          <div className="flex items-center space-x-2 mb-1">
            <span
              className="w-2.5 h-2.5 rounded-full"
              style={{ backgroundColor: TYPE_STYLES[tooltip.data.type as keyof typeof TYPE_STYLES].color }}
            />
            <span className="font-bold text-slate-800 text-sm">{tooltip.data.name}</span>
          </div>
          <p className="text-xs text-slate-500 font-semibold mb-2">{TYPE_STYLES[tooltip.data.type as keyof typeof TYPE_STYLES].label} ZONE</p>
          <p className="text-sm text-slate-600 leading-tight">{tooltip.data.desc}</p>
        </div>
      )}
    </div>
  );
}
