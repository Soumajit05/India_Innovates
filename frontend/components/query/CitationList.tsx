"use client";
import { useState } from "react";
import { ConfidenceBadge } from "@/components/shared/ConfidenceBadge";
import { ProvenanceTag } from "@/components/shared/ProvenanceTag";
import type { Citation } from "@/lib/types";

export function CitationList({ citations }: { citations: Citation[] }) {
  const [selectedCitation, setSelectedCitation] = useState<Citation | null>(null);

  if (!citations || citations.length === 0) return null;

  return (
    <>
      <div className="bg-white rounded-lg shadow-sm border border-slate-200">
        <div className="flex items-center justify-between p-4 border-b border-slate-200 bg-[#F4F6F9]">
          <div>
            <span className="text-xs font-bold tracking-wider text-[#0056B3] uppercase">Evidence</span>
            <h2 className="mt-1 text-lg font-bold text-[#212529]">Cited Graph Edges</h2>
          </div>
          <div className="px-3 py-1 bg-[#152A38] text-white text-xs font-bold rounded">
            {citations.length} Citations
          </div>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full text-sm text-left text-slate-700">
            <thead className="text-xs text-slate-700 uppercase bg-slate-100 border-b border-slate-200">
               <tr>
                 <th scope="col" className="px-4 py-2 font-semibold text-[#003366]">Confidence</th>
                 <th scope="col" className="px-4 py-2 font-semibold text-[#003366]">Source</th>
                 <th scope="col" className="px-4 py-2 font-semibold text-[#003366]">Edge Proposition</th>
                 <th scope="col" className="px-4 py-2 font-semibold text-[#003366] text-center">Action</th>
               </tr>
            </thead>
            <tbody>
               {citations.map((citation, idx) => (
                 <tr key={citation.edge_id} className={`border-b border-slate-200 hover:bg-slate-50 transition-colors ${idx % 2 === 0 ? 'bg-white' : 'bg-slate-50/50'}`}>
                   <td className="px-4 py-2 whitespace-nowrap">
                     <ConfidenceBadge value={citation.strength} />
                   </td>
                   <td className="px-4 py-2 whitespace-nowrap">
                     <ProvenanceTag url={citation.source_url} />
                   </td>
                   <td className="px-4 py-2 text-xs truncate max-w-[200px] hover:max-w-none hover:whitespace-normal transition-all" title={citation.label}>
                     {citation.label}
                   </td>
                   <td className="px-4 py-2 text-center">
                     <button 
                       onClick={() => setSelectedCitation(citation)}
                       className="text-[#0056B3] hover:text-[#004494] font-medium text-xs hover:underline"
                     >
                       View
                     </button>
                   </td>
                 </tr>
               ))}
            </tbody>
          </table>
        </div>
      </div>

      {selectedCitation && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/40 backdrop-blur-sm transition-opacity">
          <div className="bg-white rounded-lg shadow-xl w-full max-w-lg overflow-hidden animate-in fade-in zoom-in-95 duration-200">
             <div className="bg-[#152A38] px-6 py-4 flex items-center justify-between text-white">
                <h3 className="font-bold text-base">Citation Evidence</h3>
                <button onClick={() => setSelectedCitation(null)} className="text-slate-300 hover:text-white transition-colors">&times;</button>
             </div>
             <div className="p-6 space-y-4">
                <div className="flex flex-wrap items-center gap-3 border-b border-slate-100 pb-4">
                  <ConfidenceBadge value={selectedCitation.strength} />
                  <ProvenanceTag url={selectedCitation.source_url} />
                </div>
                <div>
                   <h4 className="text-sm font-bold tracking-wider text-slate-500 uppercase mb-2">Proposition / Extract</h4>
                   <p className="text-slate-700 leading-relaxed text-sm bg-slate-50 p-4 rounded border border-slate-200">{selectedCitation.label}</p>
                </div>
                <div className="pt-2">
                   <a 
                     href={selectedCitation.source_url} 
                     target="_blank" 
                     rel="noreferrer" 
                     className="block w-full text-center text-white bg-[#0056B3] hover:bg-[#004494] rounded py-2 text-sm font-medium transition-colors"
                   >
                     Visit Original Source
                   </a>
                </div>
             </div>
          </div>
        </div>
      )}
    </>
  );
}
