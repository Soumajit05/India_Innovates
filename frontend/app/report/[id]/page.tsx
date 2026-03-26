import Link from "next/link";
import { CheckCircle2, ChevronRight, FileOutput, ShieldCheck } from "lucide-react";

export default function ReportPage({ params }: { params: { id: string } }) {
  const title = params.id
    .split("-")
    .map((part) => part.charAt(0).toUpperCase() + part.slice(1))
    .join(" ");

  return (
    <div className="max-w-5xl mx-auto space-y-6">
      {/* GIGW Stepper UI */}
      <div className="bg-white rounded-lg shadow-sm border border-slate-200 p-6 mb-6">
        <h2 className="text-lg font-bold text-[#003366] mb-6">Report Generation Pipeline</h2>
        <div className="flex items-center justify-between relative">
           <div className="absolute left-0 top-1/2 -translate-y-1/2 w-full h-1 bg-slate-200 z-0 rounded"></div>
           
           <div className="relative z-10 flex flex-col items-center">
             <div className="w-10 h-10 rounded-full bg-[#28A745] text-white flex items-center justify-center font-bold border-4 border-white shadow-sm">
               <CheckCircle2 className="w-5 h-5" />
             </div>
             <span className="mt-2 text-xs font-bold text-slate-700 uppercase">1. Parameters</span>
           </div>

           <div className="relative z-10 flex flex-col items-center">
             <div className="w-10 h-10 rounded-full bg-[#0056B3] text-white flex items-center justify-center font-bold border-4 border-white shadow-sm">
               2
             </div>
             <span className="mt-2 text-xs font-bold text-[#0056B3] uppercase">2. Generation</span>
           </div>

           <div className="relative z-10 flex flex-col items-center">
             <div className="w-10 h-10 rounded-full bg-slate-200 text-slate-500 flex items-center justify-center font-bold border-4 border-white shadow-sm">
               3
             </div>
             <span className="mt-2 text-xs font-bold text-slate-500 uppercase">3. Verification</span>
           </div>
        </div>
      </div>

      <div className="bg-white rounded-lg shadow-sm border border-slate-200 p-8">
        <div className="border-b border-slate-100 pb-4 flex items-center justify-between">
          <div>
            <p className="text-xs font-bold tracking-wider text-[#0056B3] uppercase flex items-center gap-2">
              <FileOutput className="w-4 h-4" /> Strategic Report Draft
            </p>
            <h1 className="mt-2 text-3xl font-bold text-[#212529]">{title}</h1>
          </div>
          <div className="bg-[#FFC107]/20 text-yellow-800 border border-[#FFC107]/50 px-3 py-1 rounded text-xs font-bold uppercase tracking-wide">
            Draft Mode
          </div>
        </div>
        
        <div className="mt-6 text-slate-700 leading-relaxed space-y-4">
          <p>
            This route is reserved for generated strategic briefs. As the backend evolves from in-memory storage to persistent report generation, this page will formally archive query outputs, scenario packages, and judge-demo snapshots.
          </p>
        </div>

        <div className="mt-8 rounded-lg border border-slate-200 bg-[#F4F6F9] p-6">
          <h3 className="font-bold text-[#003366] flex items-center gap-2">
            <ShieldCheck className="w-5 h-5 text-[#28A745]" /> Standard Operating Procedure (SOP) Sections
          </h3>
          <ul className="mt-4 space-y-3 text-sm leading-6 text-slate-700 font-medium">
            <li className="flex items-center gap-2"><ChevronRight className="w-4 h-4 text-[#0056B3]"/> Strategic assessment with overall confidence scoring</li>
            <li className="flex items-center gap-2"><ChevronRight className="w-4 h-4 text-[#0056B3]"/> Cross-domain key findings and contradiction handling</li>
            <li className="flex items-center gap-2"><ChevronRight className="w-4 h-4 text-[#0056B3]"/> Immediate India implications and infrastructural vulnerabilities</li>
            <li className="flex items-center gap-2"><ChevronRight className="w-4 h-4 text-[#0056B3]"/> Chain of Evidence appendix with strict source provenance</li>
          </ul>
        </div>

        <div className="mt-8 flex justify-end gap-4 border-t border-slate-100 pt-6">
          <Link href="/query" className="px-6 py-2 rounded-md border border-slate-300 text-slate-700 font-medium hover:bg-slate-50 transition-colors">
            Return to Query
          </Link>
          <button className="px-6 py-2 rounded-md bg-[#0056B3] text-white font-medium hover:bg-[#004494] transition-colors shadow-sm">
            Proceed to Verification
          </button>
        </div>
      </div>
    </div>
  );
}
