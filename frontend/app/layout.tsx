import Link from "next/link";
import type { Metadata } from "next";
import type { ReactNode } from "react";
import { Home, Search, Activity, Network, Bell, FileText, UserCircle, LogOut } from "lucide-react";

import "./globals.css";

export const metadata: Metadata = {
  title: "ARGOS Dashboard | Dashboard",
  description: "Adaptive Reasoning & Global Ontology System - Government Analytics",
};

const navItems = [
  { href: "/", label: "Dashboard", Icon: Home },
  { href: "/query", label: "Query", Icon: Search },
  { href: "/graph", label: "Graph", Icon: Network },
  { href: "/alerts", label: "Alerts", Icon: Bell },
  { href: "/report", label: "Report", Icon: FileText },
  { href: "/scenarios", label: "Scenarios", Icon: Activity },
];

export default function RootLayout({ children }: { children: ReactNode }) {
  // Simplified active route handling by relying on Next.js standard Link behavior or client components.
  // For the sake of this layout without client state, we'll design the visual skeleton.
  return (
    <html lang="en">
      <body className="bg-slate-50 text-slate-800 min-h-screen flex flex-col font-sans">
        {/* Tier 1 Header: Accessibility Ribbon */}
        <div className="bg-[#152A38] text-white h-10 flex items-center justify-between px-6 text-sm">
          <div className="flex items-center gap-4">
            <span className="font-semibold text-xs tracking-wider">GOVERNMENT OF INDIA</span>
          </div>
          <div className="flex items-center gap-6">
            <button className="hover:underline focus:ring-2 focus:ring-white outline-none">Skip to Main Content</button>
            <div className="flex items-center gap-2">
              <span className="mr-2">Text Size</span>
              <button className="hover:text-blue-200">A-</button>
              <button className="font-bold hover:text-blue-200">A</button>
              <button className="hover:text-blue-200">A+</button>
            </div>
            <button className="hover:underline focus:ring-2 focus:ring-white outline-none">High Contrast</button>
          </div>
        </div>

        {/* Tier 2 Header: Brand Identity Ribbon */}
        <header className="bg-white border-b-[3px] border-b-transparent relative" style={{ borderImage: 'linear-gradient(to right, #FF9933 0%, #FFFFFF 50%, #138808 100%)', borderImageSlice: 1 }}>
          <div className="flex items-center justify-between px-6 py-4">
            <div className="flex items-center gap-4">
              <div className="flex h-12 w-12 items-center justify-center rounded-lg bg-[#0056B3] font-bold text-xl text-white shadow-sm">
                AR
              </div>
              <div>
                <h1 className="text-2xl font-bold text-[#003366] leading-none mb-1">ANTIGRAVITY</h1>
                <p className="text-xs font-semibold text-slate-500 uppercase tracking-widest">Intelligence Dashboard</p>
              </div>
            </div>
            <div className="flex-1 max-w-xl mx-8">
              <div className="relative">
                <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400 h-4 w-4" />
                <input 
                  type="text" 
                  placeholder="Global Search..." 
                  className="w-full bg-slate-100 border border-slate-300 text-slate-800 text-sm rounded-md pl-10 pr-4 py-2 focus:outline-none focus:ring-2 focus:ring-[#0056B3]"
                />
              </div>
            </div>
            <div className="flex items-center gap-4 text-slate-700">
               <button className="flex items-center gap-2 hover:text-[#0056B3]">
                 <UserCircle className="h-6 w-6" />
                 <span className="font-medium text-sm">Profile</span>
               </button>
               <div className="w-px h-6 bg-slate-300"></div>
               <button className="flex items-center gap-2 hover:text-red-600 text-sm font-medium">
                 <LogOut className="h-4 w-4" />
                 Logout
               </button>
            </div>
          </div>
        </header>

        <div className="flex flex-1 overflow-hidden">
          {/* Sidebar Navigation */}
          <aside className="w-64 bg-white border-r border-slate-200 shadow-sm flex flex-col pt-6 z-10 sticky top-0 h-[calc(100vh-130px)]">
            <div className="px-4 mb-4">
               <span className="text-xs font-bold text-slate-400 uppercase tracking-wider">Main Menu</span>
            </div>
            <nav className="flex-1 flex flex-col px-3 gap-1">
              {navItems.map((item) => {
                const isDashboard = item.href === "/";
                // For simplicity in static layout, highlighting /graph as example or rely on active state logic in a client component. 
                // We'll give active state logic wrapper to components if needed, or just standard links.
                return (
                  <Link
                    key={item.href}
                    href={item.href}
                    className="flex items-center gap-3 px-3 py-3 rounded-md text-sm font-medium text-slate-700 hover:bg-[#0056B3]/10 hover:text-[#0056B3] transition-colors border-l-4 border-transparent hover:border-[#0056B3]"
                  >
                    <item.Icon className="h-5 w-5" />
                    {item.label}
                  </Link>
                );
              })}
            </nav>
          </aside>

          {/* Main Content Area */}
          <main className="flex-1 overflow-auto bg-[#F4F6F9] p-6 lg:p-8 relative">
            {children}
          </main>
        </div>

        {/* Standardized Footer */}
        <footer className="bg-[#003366] text-white py-6 mt-auto">
          <div className="max-w-7xl mx-auto px-6 flex flex-col md:flex-row items-center justify-between gap-4 text-sm">
            <div className="text-slate-300">
              <Link href="#" className="hover:text-white mr-4">Terms & Conditions</Link>
              <Link href="#" className="hover:text-white mr-4">Privacy Policy</Link>
              <Link href="#" className="hover:text-white mr-4">Accessibility Statement</Link>
              <Link href="#" className="hover:text-white">Help</Link>
            </div>
            <div className="text-slate-300 text-xs">
              Page Last Updated: {new Date().toLocaleDateString('en-GB', { day: '2-digit', month: 'short', year: 'numeric' })}
            </div>
            <div className="text-slate-300 text-xs bg-[#152A38] px-3 py-1 rounded">
              Visitors: <span className="font-mono">001,459,203</span>
            </div>
          </div>
        </footer>
      </body>
    </html>
  );
}
