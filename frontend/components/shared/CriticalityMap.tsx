"use client";

import { useState } from "react";
import { AlertCircle, AlertTriangle, Info, CheckCircle2 } from "lucide-react";

export type CriticalityLevel = "LOW" | "MEDIUM" | "HIGH" | "CRITICAL";

export interface MapNode {
  id: string;
  coordinates: [number, number]; // [x, y] percentage mapping (0-100)
  title: string;
  criticality: CriticalityLevel;
  reason: string;
}

const mockNodes: MapNode[] = [
  { id: "n1", coordinates: [20, 30], title: "Primary Database Server", criticality: "CRITICAL", reason: "Unusual traffic spike detected at 0400 hours." },
  { id: "n2", coordinates: [60, 45], title: "Sector Alpha Firewall", criticality: "HIGH", reason: "Multiple unauthorized access attempts blocked outside expected operational parameters." },
  { id: "n3", coordinates: [80, 20], title: "Storage Array C", criticality: "MEDIUM", reason: "Disk latency increasing, potential hardware degradation signaling." },
  { id: "n4", coordinates: [40, 70], title: "Web Cache Layer", criticality: "LOW", reason: "Acting nominally, routine updates successfully applied." },
  { id: "n5", coordinates: [75, 80], title: "Backup Controller", criticality: "CRITICAL", reason: "Sync failure with offsite repository for 12 hours straight." },
];

const criticalityStyles = {
  CRITICAL: { bg: "bg-red-600", text: "text-red-600", pulse: true, Icon: AlertCircle },
  HIGH:     { bg: "bg-orange-500", text: "text-orange-500", pulse: false, Icon: AlertTriangle },
  MEDIUM:   { bg: "bg-yellow-400", text: "text-yellow-600", pulse: false, Icon: Info },
  LOW:      { bg: "bg-slate-400", text: "text-slate-500", pulse: false, Icon: CheckCircle2 },
};

export function CriticalityMap() {
  const [hoveredNode, setHoveredNode] = useState<MapNode | null>(null);
  const [tooltipPos, setTooltipPos] = useState({ x: 0, y: 0 });

  const handleMouseEnter = (e: React.MouseEvent, node: MapNode) => {
    setHoveredNode(node);
    setTooltipPos({ x: e.clientX, y: e.clientY });
  };

  const handleMouseMove = (e: React.MouseEvent) => {
    if (hoveredNode) {
      setTooltipPos({ x: e.clientX, y: e.clientY });
    }
  };

  const handleMouseLeave = () => {
    setHoveredNode(null);
  };

  return (
    <div 
      className="relative w-full h-[400px] bg-slate-50 border border-slate-200 rounded-lg overflow-hidden shadow-sm"
      onMouseMove={handleMouseMove}
    >
      {/* Background Grid Pattern */}
      <div 
        className="absolute inset-0 z-0 opacity-10" 
        style={{ backgroundImage: 'radial-gradient(circle at 1px 1px, #152A38 1px, transparent 0)', backgroundSize: '24px 24px' }} 
      />
      
      {/* Map Nodes Layer */}
      {mockNodes.map((node) => {
        const style = criticalityStyles[node.criticality];
        return (
          <div
            key={node.id}
            className="absolute z-10 cursor-crosshair -translate-x-1/2 -translate-y-1/2 group"
            style={{ left: `${node.coordinates[0]}%`, top: `${node.coordinates[1]}%` }}
            onMouseEnter={(e) => handleMouseEnter(e, node)}
            onMouseLeave={handleMouseLeave}
          >
            <div className="relative flex items-center justify-center p-2">
              {style.pulse && (
                <div className={`absolute inset-0 rounded-full ${style.bg} opacity-40 animate-ping`} />
              )}
              <div className={`relative w-4 h-4 rounded-full border-2 border-white shadow-sm transition-transform group-hover:scale-125 ${style.bg}`} />
            </div>
          </div>
        );
      })}

      {/* Tooltip Overlay */}
      {hoveredNode && (() => {
        const HoveredIcon = criticalityStyles[hoveredNode.criticality].Icon;
        return (
          <div
            className="fixed z-50 pointer-events-none"
            style={{ left: tooltipPos.x + 16, top: tooltipPos.y + 16 }}
          >
            <div className="bg-white rounded-md shadow-lg border border-slate-200 p-3 w-64 animate-in fade-in zoom-in-95 duration-100">
              <div className="flex items-center gap-2 border-b border-slate-100 pb-2 mb-2">
                <div className={criticalityStyles[hoveredNode.criticality].text}>
                  <HoveredIcon className="w-4 h-4" />
                </div>
                <span className="font-bold text-sm text-[#212529] truncate">{hoveredNode.title}</span>
              </div>
              <p className="text-xs text-slate-700 leading-relaxed font-medium">
                {hoveredNode.reason}
              </p>
            </div>
          </div>
        );
      })()}
    </div>
  );
}
